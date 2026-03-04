# 毫米波整合開發專案 (mmWave Project)

本倉庫包含兩個主要部分：一個是運行在 Windows/Linux 上的毫米波後端處理程式，另一個是運行在 Mac 上的 iOS/macOS 應用程式。

---

## 📂 專案結構

- **mmWave/**: 毫米波核心處理程式 (Windows/Python 環境)
- **mmWave_APP/**: 專案專屬行動裝置 App (Mac/Xcode 環境)

---

## 🚀 毫米波後端程式 (mmWave)

負責毫米波雷達數據的讀取與處理。

### 開啟方式
- **程式入口**: `mmWave/route.py`
- **執行環境**: Python 3.x
- **執行指令**:
  ```bash
  cd mmWave
  python route.py
