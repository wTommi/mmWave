import Foundation

// 確保這跟伺服器回傳的 JSON 格式一致
struct MmWaveResponse: Codable {
    let confidence: String
    let prediction: String
}

class MmWaveManager {
    
    private var timer: Timer?
    private var isMonitoring = false
    private var isFetching = false
    
    func startMonitoring() {
        stopMonitoring()
        
        isMonitoring = true
        
        print("📡 MmWaveManager: 啟動監聽...")

        timer = Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { [weak self] _ in
            self?.getMmWaveData()
        }
    }
    
    // 停止監聽
    func stopMonitoring() {
        
        isMonitoring = false
        
        if timer != nil {
            print("💤 MmWaveManager: 停止監聽")
            timer?.invalidate()
            timer = nil
        }
    }
    
    private func getMmWaveData() {
        
        guard !isFetching else { return }
        
        guard let url = URL(string: "http://192.168.194.2:5000/get_mmwave") else { return }

        isFetching = true // 上鎖
        
        let task = URLSession.shared.dataTask(with: url) { [weak self] data, _, error in
            
            defer {
                self?.isFetching = false // 解鎖
            }
            
            guard let safeData = data, error == nil else { return }
            
            DispatchQueue.main.async {
                guard let self = self, self.isMonitoring else {
                    return
                }
                do {
                    let result = try JSONDecoder().decode(MmWaveResponse.self, from: safeData)
                    
                    if result.prediction == "background" {
                        MmWaveDataStore.shared.label = "Safe"
                    } else {
                        MmWaveDataStore.shared.label = result.prediction
                    }
                } catch {
                    print("⚠️ mmWave JSON 解析失敗: \(error)")
                }
            }
        }
        task.resume()
    }
}
