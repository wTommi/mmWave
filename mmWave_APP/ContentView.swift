import SwiftUI
import Combine
import AVFoundation
import MapKit

// MARK: - 1. 橋接器 (負責把 ViewController 拉進來並控制它)
struct CameraBridge: UIViewControllerRepresentable {
    @Binding var isRecording: Bool
    
    func makeUIViewController(context: Context) -> ViewController {
        let vc = ViewController()
        let _ = vc.view // 強制載入視圖
        return vc
    }
    
    func updateUIViewController(_ uiViewController: ViewController, context: Context) {
        uiViewController.isRecording = isRecording
    }
}

// MARK: - 2. 狀態定義與 ViewModel
enum RecordingStatus {
    case ready
    case recording
    case stopped
}

@MainActor
class RecorderViewModel: NSObject, ObservableObject {
    
    @Published var isRecording = false
    @Published var recordingStatus: RecordingStatus = .ready // 取代原本的字串，改用狀態管理
    @Published var isEnglish = false
    
    private let mmWaveManager = MmWaveManager()
    
    func configureAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .playback,
                mode: .default,
                options: [.duckOthers]
            )
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("音訊設定失敗: \(error)")
        }
    }

    func toggleRecording() {
        isRecording.toggle()
        
        if isRecording {
            configureAudioSession()
            SpeechManager.shared.speak(isEnglish ? "Recording started" : "開始錄影", isEnglish: isEnglish)
            recordingStatus = .recording
            mmWaveManager.startMonitoring()
        } else {
            SpeechManager.shared.speak(isEnglish ? "Recording stopped" : "錄影已停止", isEnglish: isEnglish)
            recordingStatus = .stopped
            mmWaveManager.stopMonitoring()
            
            // 資料統一重置為英文標籤，畫面端會自動根據 isEnglish 翻譯成「無」
            MmWaveDataStore.shared.traffic_light = "None"
            MmWaveDataStore.shared.label = "None"
        }
    }
}

// MARK: - 3. 主畫面 (ContentView)
struct ContentView: View {
    
    // State & ViewModels
    @StateObject private var viewModel = RecorderViewModel()
    @StateObject private var locationManager = LocationManager()
    @ObservedObject var dataStore = MmWaveDataStore.shared
    
    // UI States
    @State private var showMap = false 
    @State private var cameraPosition: MapCameraPosition = .userLocation(followsHeading: true, fallback: .automatic)
    
    // Haptics & Timers
    @State private var hapticTimer: Timer? = nil
    @State private var impactGenerator = UIImpactFeedbackGenerator(style: .medium)
    
    var body: some View {
        VStack {
            headerSection
            
            Spacer()
            
            mapAndCameraSection
            
            Spacer()
            
            dataAndControlsSection
            
            Spacer()
        }
        // 監聽數值變化以觸發震動與語音
        .onChange(of: dataStore.label) { oldValue, newValue in
            updateDistanceHaptics(label: newValue)
        }
        .onChange(of: dataStore.traffic_light) { oldValue, newValue in
            updateTrafficLightFeedback(light: newValue)
        }
    }
}

// MARK: - 4. 畫面區塊 (ViewBuilders) 拆分，提升可讀性
extension ContentView {
    
    // 區塊 A: 頂部標題與語言切換
    private var headerSection: some View {
        VStack {
            Text(viewModel.isEnglish ? "Guide Assistant System" : "導盲輔助系統")
                .font(.system(size: 30, weight: .heavy))
                .fontWeight(.heavy)
                .foregroundColor(.black)
                .padding(.top, 20)
            
            HStack {
                Image(systemName: "speaker.wave.2.circle.fill")
                    .font(.largeTitle)
                
                // 語言切換按鈕
                ZStack {
                    Capsule()
                        .fill(Color(.systemGray5))
                        .frame(width: 100, height: 40)
                    
                    HStack {
                        if viewModel.isEnglish { Spacer() }
                        Capsule()
                            .fill(Color.white)
                            .frame(width: 46, height: 36)
                            .shadow(color: .black.opacity(0.2), radius: 2, x: 0, y: 1)
                            .padding(.horizontal, 2)
                        if !viewModel.isEnglish { Spacer() }
                    }
                    
                    HStack(spacing: 0) {
                        Text("中")
                            .font(.system(size: 16, weight: .bold))
                            .frame(width: 50)
                            .foregroundColor(viewModel.isEnglish ? .gray : .black)
                        
                        Text("英")
                            .font(.system(size: 16, weight: .bold))
                            .frame(width: 50)
                            .foregroundColor(viewModel.isEnglish ? .black : .gray)
                    }
                }
                .frame(width: 100, height: 40)
                .onTapGesture {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                        viewModel.isEnglish.toggle()
                    }
                    UIImpactFeedbackGenerator(style: .light).impactOccurred()
                }
                .padding(.trailing, 20)
            }
        }
    }
    
    // 區塊 B: 地圖與相機預覽
    private var mapAndCameraSection: some View {
        ZStack(alignment: .topTrailing) {
            Map(position: $cameraPosition) {
                UserAnnotation()
                if !locationManager.pathCoordinates.isEmpty {
                    MapPolyline(coordinates: locationManager.pathCoordinates)
                        .stroke(.blue, style: StrokeStyle(lineWidth: 5, lineCap: .round, lineJoin: .round))
                }
            }
            .opacity(showMap ? 1.0 : 0.0)
            .allowsHitTesting(showMap)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            
            if !showMap {
                CameraBridge(isRecording: $viewModel.isRecording)
            }
            
            // 地圖/相機切換按鈕
            Button {
                showMap.toggle()
            } label: {
                Image(systemName: showMap ? "map" : "camera")
                    .font(.system(size: 30))
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.black)
                    .clipShape(Circle())
            }
            .padding(10)
        }
        .frame(maxWidth: .infinity)
        .frame(height: 300)
        .cornerRadius(20)
        .padding(.horizontal)
        .shadow(radius: 5)
    }
    
    // 區塊 C: 數據卡片與控制按鈕
    private var dataAndControlsSection: some View {
        VStack(spacing: 30) {
            HStack {
                // 燈號卡片 (套用翻譯函式)
                DataCardView(
                    title: viewModel.isEnglish ? "Traffic Light" : "燈號",
                    value: localizedTrafficLight(dataStore.traffic_light, isEnglish: viewModel.isEnglish),
                    color: colorForTrafficLight(dataStore.traffic_light)
                )
                // 距離卡片 (套用翻譯函式)
                DataCardView(
                    title: viewModel.isEnglish ? "Distance" : "距離",
                    value: localizedDistance(dataStore.label, isEnglish: viewModel.isEnglish),
                    color: .blue
                )
            }
            
            // 狀態提示文字 (即時翻譯)
            Text(statusMessageText)
                .multilineTextAlignment(.center)
                .font(.body)
                .foregroundColor(.gray)
                .padding(.top, 40)
            
            // 錄影控制按鈕
            Button(action: {
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.prepare()
                generator.impactOccurred()
                viewModel.toggleRecording()
            }) {
                Text(buttonTitle)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .frame(width: 250, height: 60)
                    .background(viewModel.isRecording ? Color.red : Color.blue)
                    .cornerRadius(15)
                    .shadow(radius: 5)
            }
        }
        .padding()
    }
}

// MARK: - 5. 動態文字計算與輔助函式 (Helper Functions)
extension ContentView {
    
    // 計算錄影按鈕文字
    private var buttonTitle: String {
        if viewModel.isRecording {
            return viewModel.isEnglish ? "Stop Recording" : "停止錄影"
        } else {
            return viewModel.isEnglish ? "Start Recording" : "開始背景錄影"
        }
    }
    
    // 計算狀態提示文字
    private var statusMessageText: String {
        switch viewModel.recordingStatus {
        case .ready:
            return viewModel.isEnglish ? "Ready" : "準備就緒"
        case .recording:
            return viewModel.isEnglish ? "Recording in background...\n(Processing on device)" : "正在背景錄影...\n(畫面傳到嵌入式設備作處理)"
        case .stopped:
            return viewModel.isEnglish ? "Recording stopped" : "錄影已停止"
        }
    }
    
    // 燈號文字翻譯
    func localizedTrafficLight(_ light: String, isEnglish: Bool) -> String {
        let normalized = light.lowercased()
        if normalized.contains("red") {
            return isEnglish ? "Red" : "紅燈"
        } else if normalized.contains("green") {
            return isEnglish ? "Green" : "綠燈"
        } else if normalized.contains("none") {
            return isEnglish ? "None" : "無"
        }
        return light
    }
    
    // 距離文字翻譯
    func localizedDistance(_ label: String, isEnglish: Bool) -> String {
        let normalized = label.lowercased()
        if normalized.contains("close") {
            return isEnglish ? "Close" : "近"
        } else if normalized.contains("far") {
            return isEnglish ? "Far" : "遠"
        } else if normalized.contains("safe") {
            return isEnglish ? "Safe" : "安全"
        } else if normalized.contains("none") {
            return isEnglish ? "None" : "無"
        }
        return label
    }
    
    // 燈號顏色判斷
    func colorForTrafficLight(_ light: String) -> Color {
        let normalizedLight = light.lowercased()
        if normalizedLight.contains("red") {
            return .red
        } else if normalizedLight.contains("green") {
            return .green
        } else {
            return .gray
        }
    }
    
    // 燈號語音回饋
    func updateTrafficLightFeedback(light: String) {
        guard viewModel.isRecording else { return }
        let normalizedLight = light.lowercased()
        
        if normalizedLight.contains("red") {
            SpeechManager.shared.speak(viewModel.isEnglish ? "Red light, do not cross." : "現在是紅燈，請勿通行", isEnglish: viewModel.isEnglish)
        } else if normalizedLight.contains("green") {
            SpeechManager.shared.speak(viewModel.isEnglish ? "Green light, safe to go." : "現在是綠燈", isEnglish: viewModel.isEnglish)
        }
    }
    
    // 距離震動回饋
    func updateDistanceHaptics(label: String) {
        hapticTimer?.invalidate()
        hapticTimer = nil
        
        guard viewModel.isRecording else { return }
        
        if label.contains("Close") {
            SpeechManager.shared.speak(viewModel.isEnglish ? "Too Close, Stop!" : "距離太近, 注意安全", isEnglish: viewModel.isEnglish)
            impactGenerator = UIImpactFeedbackGenerator(style: .heavy)
            impactGenerator.prepare()
            DispatchQueue.main.async { self.impactGenerator.impactOccurred() }
            startHighFrequencyHaptics(interval: 0.2, style: .heavy)
        } else if label.contains("Far") {
            SpeechManager.shared.speak(viewModel.isEnglish ? "Obstacle ahead" : "前方有障礙物", isEnglish: viewModel.isEnglish)
            impactGenerator = UIImpactFeedbackGenerator(style: .light)
            impactGenerator.prepare()
            DispatchQueue.main.async { self.impactGenerator.impactOccurred() }
            startHighFrequencyHaptics(interval: 0.6, style: .light)
        } else if label.contains("Safe") {
            hapticTimer?.invalidate()
            hapticTimer = nil
        }
    }
    
    func startHighFrequencyHaptics(interval: Double, style: UIImpactFeedbackGenerator.FeedbackStyle) {
        hapticTimer?.invalidate()
        hapticTimer = nil
        hapticTimer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { _ in
            let generator = UIImpactFeedbackGenerator(style: style)
            generator.prepare()
            generator.impactOccurred()
        }
        if let hapticTimer = hapticTimer {
            RunLoop.main.add(hapticTimer, forMode: .common)
        }
    }
}

// MARK: - 6. 子視圖 (Subviews)
struct DataCardView: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(title)
                .font(.headline)
                .foregroundColor(.black)
                .opacity(0.7)
            
            Text(value)
                .font(.system(size: 35, weight: .bold, design: .rounded))
                .foregroundColor(color)
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
        .shadow(color: Color.black.opacity(0.1), radius: 3, x: 0, y: 2)
        .frame(maxWidth: .infinity, maxHeight: 10)
    }
}

#Preview {
    ContentView()
}
