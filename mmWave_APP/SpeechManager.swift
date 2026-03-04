import AVFoundation

class SpeechManager {

    static let shared = SpeechManager()
    
    private let synthesizer = AVSpeechSynthesizer()

    func speak(_ text: String, isEnglish: Bool = false) {

        let utterance = AVSpeechUtterance(string: text)

        if isEnglish {
            utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        } else {
            utterance.voice = AVSpeechSynthesisVoice(language: "zh-TW") 
        }
        
        // 4. 設定語速 (0.0 ~ 1.0, 預設 0.5)
        utterance.rate = 0.55
        
        // 5. 設定音調 (0.5 ~ 2.0)
        utterance.pitchMultiplier = 1.0
        
        utterance.volume = 0.25
        
        // 6. 開始說話
        synthesizer.speak(utterance)
    }
    
    // 停止說話 (例如按下停止錄影時)
    func stop() {
        if synthesizer.isSpeaking {
            synthesizer.stopSpeaking(at: .immediate)
        }
    }
}
