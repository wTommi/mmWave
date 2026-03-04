# 檔案名稱：online_inference_gui.py (請確保檔名與 route.py 匯入一致)
import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- 保留你原本的模型與參數定義 (省略重複代碼) ---
MODEL_PATH = r"3d_cnn_model.pth"
SETTING_FILE = r"K60168-Test-00256-008-v0.0.8-20230717_480cm"
WINDOW_SIZE = 30
CLASS_NAMES = ["background", "Close", "Far"]
CLASS_NUM = len(CLASS_NAMES)
ENTER_TH = 0.40
EXIT_TH = 0.20
STREAM_TYPE = "feature_map"

from KKT_Module import kgl
from KKT_Module.DataReceive.Core import Results
from KKT_Module.DataReceive.DataReceiver import MultiResult4168BReceiver
from KKT_Module.FiniteReceiverMachine import FRM
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc
from KKT_Module.GuiUpdater.GuiUpdater import Updater

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


class OnlineInferenceContext:
    def __init__(self, model, device, window):
        self.model = model
        self.device = device
        self.window = window
        self.buffer = np.zeros((2, 32, 32, window), dtype=np.float32)
        self.collected = 0

    @staticmethod
    def to_frame(arr):
        x = np.asarray(arr)
        if x.shape == (32,32,2):
            x = np.transpose(x, (2,0,1))
        return x.astype(np.float32)

    def push_and_infer(self, frame):
        if frame.shape == (32, 32, 2): frame = np.transpose(frame, (2, 0, 1))
        self.buffer = np.roll(self.buffer, shift=-1, axis=-1)
        self.buffer[..., -1] = frame
        if self.collected < self.window:
            self.collected += 1
            return None
        input_data = np.expand_dims(np.transpose(self.buffer, (0, 3, 1, 2)), axis=0)
        x = torch.from_numpy(input_data).float().to(self.device)
        with torch.no_grad():
            return self.model(x).cpu().numpy()[0]

    def select_class(self, probs):
        idx = np.argmax(probs)
        return CLASS_NAMES[idx], probs[idx]

# ========== 🔥 關鍵修改：SharedDataUpdater ==========
# ========== 修改後的 SharedDataUpdater (除錯版) ==========
class SharedDataUpdater(Updater):
    def __init__(self, ctx, shared_dict):
        super().__init__()
        self.ctx = ctx
        self.data = shared_dict

    def update(self, res: Results):
        if not hasattr(res, "feature_map"):
            print(f"DEBUG: 收到資料但沒有 feature_map")
            return
        
        arr = res['feature_map'].data
        frame = self.ctx.to_frame(arr)

        probs = self.ctx.push_and_infer(frame)
        
        if probs is None: 
            return 

        current, val = self.ctx.select_class(probs)
        
        self.data["prediction"] = current
        self.data["confidence"] = str(round(float(val), 2))

        print(f"🚀 偵測成功: {current} (信心度: {val:.2f})")
        
# ========== 啟動函式 (給 Flask 呼叫) ==========
def start_mmwave(shared_dict):
    kgl.setLib()
    try:
        kgl.ksoclib.connectDevice()
    except:
        print("❌ 毫米波連線失敗")
        return

    # 硬體設定
    ksp = SettingProc()
    cfg = SettingConfigs()
    try:
        cfg.Chip_ID = kgl.ksoclib.getChipID().split(' ')[0]
    except:
        cfg.Chip_ID = "Unknown"
    cfg.Processes = ['Reset Device', 'Gen Process Script', 'Set Script', 'Run SIC', 'Modulation On']
    cfg.setScriptDir(SETTING_FILE)
    ksp.startUp(cfg)

    # 模型載入
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Gesture3DCNN(num_classes=CLASS_NUM).to(device)
    if os.path.exists(MODEL_PATH):
        state = torch.load(MODEL_PATH, map_location=device)
        model.load_state_dict(state, strict=False)
        model.eval()
    else:
        print("❌ 找不到模型")
        return

    # 建立 Updater (傳入 shared_dict)
    ctx = OnlineInferenceContext(model, device, WINDOW_SIZE)
    updater = SharedDataUpdater(ctx, shared_dict)

    receiver = MultiResult4168BReceiver()
    FRM.setReceiver(receiver)
    FRM.setUpdater(updater)
    FRM.trigger()
    FRM.start()
    
    print("✅ 毫米波背景執行中...")
    while True: time.sleep(1) # 讓這個 Thread 卡住不要結束