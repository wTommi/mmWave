# 檔案名稱：online_inference_gui.py
import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- 核心參數定義 ---
MODEL_PATH = r"3d_cnn_model.pth"
SETTING_FILE = r"K60168-Test-00256-008-v0.0.8-20230717_480cm"
WINDOW_SIZE = 30
CLASS_NAMES = ["background", "Close", "Far"]
CLASS_NUM = len(CLASS_NAMES)
STREAM_TYPE = "feature_map"

# 載入 KKT 相關模組
from KKT_Module import kgl
from KKT_Module.DataReceive.Core import Results
from KKT_Module.DataReceive.DataReceiver import MultiResult4168BReceiver
from KKT_Module.FiniteReceiverMachine import FRM
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc
from KKT_Module.GuiUpdater.GuiUpdater import Updater


# --- 模型結構定義 ---
class Gesture3DCNN(nn.Module):
    def __init__(self, num_classes=CLASS_NUM):
        super(Gesture3DCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv3d(in_channels=2, out_channels=32, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(32),
            nn.Conv3d(32, 64, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(64),
            nn.Conv3d(64, 128, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(128),
        )
        self.global_avg_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.classifier = nn.Sequential(
            nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.5), nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        # 使用 Softmax 確保輸出為機率 (信心值)
        return torch.softmax(self.classifier(x), dim=1)

# 檔案名稱：online_inference_gui.py
import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
from collections import deque

# --- 核心參數定義 ---
MODEL_PATH = r"3d_cnn_model.pth"
SETTING_FILE = r"K60168-Test-00256-008-v0.0.8-20230717_480cm"
WINDOW_SIZE = 30
CLASS_NAMES = ["background", "Close", "Far"]
CLASS_NUM = len(CLASS_NAMES)

# --- 模型結構 (Gesture3DCNN 保持不變) ---
# 
class Gesture3DCNN(nn.Module):
    def __init__(self, num_classes=CLASS_NUM):
        super(Gesture3DCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv3d(in_channels=2, out_channels=32, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(32),
            nn.Conv3d(32, 64, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(64),
            nn.Conv3d(64, 128, kernel_size=3),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.BatchNorm3d(128),
        )
        self.global_avg_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.classifier = nn.Sequential(
            nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.5), nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        return torch.softmax(self.classifier(x), dim=1)

# --- 推論邏輯與狀態保持 ---
class OnlineInferenceContext:
    def __init__(self, model, device, window):
        self.model = model
        self.device = device
        self.window = window
        self.buffer = np.zeros((2, 32, 32, window), dtype=np.float32)
        self.collected = 0
        
        # 平滑處理：使用 deque 儲存最近 8 幀機率值
        self.smooth_window = 8 
        self.prob_history = deque(maxlen=self.smooth_window)

    @staticmethod
    def to_frame(arr):
        x = np.asarray(arr)
        if x.shape == (32, 32, 2):
            x = np.transpose(x, (2, 0, 1))
        return x.astype(np.float32)

    def push_and_infer(self, frame):
        if frame.shape == (32, 32, 2):
            frame = np.transpose(frame, (2, 0, 1))
        self.buffer = np.roll(self.buffer, shift=-1, axis=-1)
        self.buffer[..., -1] = frame

        if self.collected < self.window:
            self.collected += 1
            return None

        input_data = np.expand_dims(np.transpose(self.buffer, (0, 3, 1, 2)), axis=0)
        x = torch.from_numpy(input_data).float().to(self.device)

        with torch.no_grad():
            raw_probs = self.model(x).cpu().numpy()[0]
            self.prob_history.append(raw_probs)
            return np.mean(self.prob_history, axis=0)

    def select_class(self, probs):
        """
        修正後的邏輯：
        1. 調低手勢門檻至 0.45，增加靈敏度。
        2. 若信心度不足，回傳 None 觸發『狀態鎖定』。
        """
        bg_conf = probs[0]
        close_conf = probs[1]
        far_conf = probs[2]

        # 如果背景非常明確 (高於 0.65)，才切換回背景
        if bg_conf > 0.65:
            return CLASS_NAMES[0], bg_conf
        
        # 如果是明確的手勢 (門檻降為 0.45)
        if close_conf > 0.45 and close_conf >= far_conf:
            return CLASS_NAMES[1], close_conf
        
        if far_conf > 0.45 and far_conf > close_conf:
            return CLASS_NAMES[2], far_conf
            
        # --- 核心：模糊地帶回傳 None，SharedDataUpdater 會跳過更新 ---
        return None, None

# --- 資料更新器 (銜接硬體與 Flask) ---
class SharedDataUpdater(Updater):
    def __init__(self, ctx, shared_dict):
        super().__init__()
        self.ctx = ctx
        self.data = shared_dict
        self.last_update_time = 0
        self.update_interval = 0.3  # 每 0.3 秒嘗試更新一次路由

    def update(self, res: Results):
        if not hasattr(res, "feature_map"):
            return

        arr = res['feature_map'].data
        frame = self.ctx.to_frame(arr)
        probs = self.ctx.push_and_infer(frame)

        if probs is None:
            return

        current_name, current_val = self.ctx.select_class(probs)
        current_time = time.time()

        # ✨ 只有當判定結果明確時 (不是 None)，才更新 Flask 的資料
        if current_name is not None:
            if current_time - self.last_update_time >= self.update_interval:
                self.data["prediction"] = current_name
                self.data["confidence"] = str(round(float(current_val), 2))
                self.last_update_time = current_time

                # 偵錯印出
                print(f"✅ 更新狀態: {current_name:10s} (信心度: {current_val:.2f})")
        else:
            # 處於過渡期，保持原樣
            pass

# --- 啟動函式 ---
def start_mmwave(shared_dict):
    kgl.setLib()
    try:
        kgl.ksoclib.connectDevice()
        print("✅ 毫米波雷達已連線")
    except Exception as e:
        print(f"❌ 毫米波連線失敗: {e}")
        return

    # 硬體初始化設定
    ksp = SettingProc()
    cfg = SettingConfigs()
    try:
        cfg.Chip_ID = kgl.ksoclib.getChipID().split(' ')[0]
    except:
        cfg.Chip_ID = "Unknown"

    cfg.Processes = ['Reset Device', 'Gen Process Script', 'Set Script', 'Run SIC', 'Modulation On']
    cfg.setScriptDir(SETTING_FILE)
    ksp.startUp(cfg)

    # 模型載入與硬體加速設定
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f" usando {device} for inference")

    model = Gesture3DCNN(num_classes=CLASS_NUM).to(device)

    if os.path.exists(MODEL_PATH):
        try:
            state = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(state, strict=False)
            model.eval()
            print(f"✅ 成功載入模型權重: {MODEL_PATH}")
        except Exception as e:
            print(f"❌ 模型載入發生錯誤: {e}")
            return
    else:
        print(f"❌ 找不到模型檔案: {MODEL_PATH}")
        return

    # 建立上下文與更新器
    ctx = OnlineInferenceContext(model, device, WINDOW_SIZE)
    updater = SharedDataUpdater(ctx, shared_dict)

    # 設定 KKT 接收機制
    receiver = MultiResult4168BReceiver()
    FRM.setReceiver(receiver)
    FRM.setUpdater(updater)
    FRM.trigger()
    FRM.start()

    print("✅ 毫米波背景執行中，等待手勢觸發...")

    # 維持執行緒
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 正在停止毫米波偵測...")