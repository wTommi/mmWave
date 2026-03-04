# 毫米波整合開發專案 (mmWave Project)

本倉庫包含兩個主要部分：一個是運行在 Windows 上的毫米波數據處理後端，另一個是運行在 iOS/macOS 上的應用程式介面。

---

## 專案結構與路徑

- **`mmWave/`**: 毫米波核心處理程式 (Windows/Python)
- **`mmWave_APP/`**: 行動裝置應用程式 (Mac/Xcode)

---

## 毫米波後端程式 (Windows)

負責毫米波雷達數據的讀取、訊號處理與 API 路由。

### 開啟方式
- **主程式入口**: `mmWave/route.py`
- **執行環境**: Python 3.8
- **執行指令**:
  ```bash
  cd mmWave
  python route.py
  ```

---

## 行動應用程式 (Mac/iOS)

使用原生 Swift 與 SwiftUI 框架開發，用於視覺化與數據監控。

### 開啟與要求
- **開發環境**: **Xcode 26.3** 或更高版本
- **專案檔案**: `mmWave_APP/mmWave.xcodeproj`
- **核心組件**:
  - `ContentView.swift`: **主要 UI 容器**，定義了 App 的主介面佈局與導覽。
  - `MapView.swift`: 負責地圖資訊顯示。
  - `MmWaveDataStore.swift`: 負責數據流解析與狀態存儲。
  - `SpeechManager.swift`: 提供語音播報功能。
  - `mmWaveApp.swift`: 應用程式啟動點與主要生命週期。
  - `GetmmWave.swift`: 負責接收毫米波資料。
  - `CaptureCamera.swift`: 負責設定相機功能與接收YOLO辨識回傳結果。
    
---

## 維護紀錄
- **Xcode Version**: 26.3
- **Main Entry**: `mmWave/route.py`
- **App Entry**: `mmWave_APP/mmWaveApp.swift`
