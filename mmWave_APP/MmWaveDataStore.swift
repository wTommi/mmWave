import Foundation
import Combine

class MmWaveDataStore: ObservableObject {
    // 1. 建立單例，確保全 App 共用同一份資料
    static let shared = MmWaveDataStore()
    
    // 2. 使用 @Published，數值改變時會自動通知 UI
    @Published var traffic_light: String = "Init..."
    @Published var label: String = "Init..." // 對應 mmWave 的 prediction
    
    private init() {}
}
