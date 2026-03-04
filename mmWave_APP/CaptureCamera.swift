import AVFoundation
import UIKit

struct YoloResponse: Codable {
    let traffic_light: String
}

class ViewController: UIViewController, AVCaptureVideoDataOutputSampleBufferDelegate {
    
    var isRecording = false 
    var captureSession: AVCaptureSession!
    var backCamera: AVCaptureDevice!
    var videoPreviewLayer: AVCaptureVideoPreviewLayer!
    var previewLayer: AVCaptureVideoPreviewLayer!
    var isProcessing = false

    // 2. 時間控制與佇列
    var lastExecutionTime = Date()
    let captureInterval: TimeInterval = 1.0
    let ciContext = CIContext(options: [.useSoftwareRenderer: false])
    let processingQueue = DispatchQueue(label: "image.processing.queue")
    let videoQueue = DispatchQueue(label: "video.output.queue")
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
        setupPreviewLayer()
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession.startRunning()
        }
    }
    
    // 確保畫面大小改變時，預覽圖層會跟著變
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        if let layer = previewLayer {
            layer.frame = view.bounds
        }
    }

    func setupCamera() {
        captureSession = AVCaptureSession()
        captureSession.sessionPreset = .hd1920x1080// 或改成 .hd1920x1080 提高畫質

        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) else { return }
        backCamera = device
        
        do {
            try backCamera.lockForConfiguration()

            if backCamera.isFocusModeSupported(.continuousAutoFocus) {
                backCamera.focusMode = .continuousAutoFocus
            }
            
            if backCamera.isExposureModeSupported(.continuousAutoExposure) {
                backCamera.exposureMode = .continuousAutoExposure
            }
            
            if backCamera.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                backCamera.whiteBalanceMode = .continuousAutoWhiteBalance
            }
            
            backCamera.unlockForConfiguration()
        } catch {
            print("無法設定相機: \(error)")
        }
        
        do {
            let input = try AVCaptureDeviceInput(device: backCamera)
            if captureSession.canAddInput(input) { captureSession.addInput(input) }
        } catch { return }

        let videoDataOutput = AVCaptureVideoDataOutput()
        videoDataOutput.alwaysDiscardsLateVideoFrames = true
        videoDataOutput.setSampleBufferDelegate(self, queue: videoQueue)

        if captureSession.canAddOutput(videoDataOutput) {
            captureSession.addOutput(videoDataOutput)
            // 修正方向
            if let conn = videoDataOutput.connection(with: .video) {
                
                if conn.isVideoStabilizationSupported {
                    conn.preferredVideoStabilizationMode = .standard
                }
                
                if #available(iOS 17.0, *) {
                    if conn.isVideoRotationAngleSupported(90) { conn.videoRotationAngle = 90 }
                } else {
                    if conn.isVideoOrientationSupported { conn.videoOrientation = .portrait }
                }
            }
        }
    }
    
    func setupPreviewLayer() {
        if previewLayer == nil {
            previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            previewLayer.videoGravity = .resizeAspectFill
            view.layer.addSublayer(previewLayer)
        }
        previewLayer.frame = view.layer.bounds
    }

    // MARK: - Delegate (每 5 秒觸發)
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard isRecording else { return }
        if isProcessing { return }
        let currentTime = Date()
        if currentTime.timeIntervalSince(lastExecutionTime) >= captureInterval {
            lastExecutionTime = currentTime
            isProcessing = true
            guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
            let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
            processingQueue.async { [weak self] in
                self?.handleImageProcessing(ciImage: ciImage)
            }
        }
    }
    
    // MARK: - 處理影像 (轉檔 -> 存檔 -> 上傳)
    func handleImageProcessing(ciImage: CIImage) {
        if let cgImage = self.ciContext.createCGImage(ciImage, from: ciImage.extent) {
            
            // 轉正圖片 (相機擷取出來的通常需要旋轉，UIImage 可以處理)
            let image = UIImage(cgImage: cgImage, scale: 1.0, orientation: .up)
            
            print("✅ 1080p 截圖成功，準備儲存...")
            
            // 儲存與上傳
            if let savedURL = saveImageToDocumentDirectory(image) {
                uploadFile(fileURL: savedURL)
            }
        }
    }
    
    // MARK: - 【修正 2】補上儲存函式
    func saveImageToDocumentDirectory(_ image: UIImage) -> URL? {
        guard let docDir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else { return nil }
        let fileName = "capture_\(Int(Date().timeIntervalSince1970)).jpg"
        let fileURL = docDir.appendingPathComponent(fileName)
        
        guard let data = image.jpegData(compressionQuality: 0.5) else { return nil }
        
        do {
            try data.write(to: fileURL)
            return fileURL
        } catch {
            print("❌ 存檔失敗: \(error)")
            return nil
        }
    }
    
    // MARK: - 上傳檔案
    func uploadFile(fileURL: URL) {
        guard let serverURL = URL(string: "http://192.168.194.2:5000/upload") else { return }
        
        var request = URLRequest(url: serverURL)
        request.httpMethod = "POST"
        
        // 【修正 3】 這裡要把檔案放進 Body，不然伺服器收不到東西
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
 
        guard let fileData = try? Data(contentsOf: fileURL) else { return }
        let filename = fileURL.lastPathComponent
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        // ---------------------------------------------------------

        print("🚀 開始上傳...")
        let task = URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            
            // 無論如何都要刪除暫存檔
            defer {
                self?.deleteFile(at: fileURL)
                self?.isProcessing = false // unlock
            }
            
            if let error = error {
                print("❌ 上傳錯誤: \(error.localizedDescription)")
                return
            }
            
            if let safeData = data, let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                // 解析回傳資料 (avoid @Sendable capture of self)
                DispatchQueue.main.async {
                    guard let self = self, self.isRecording else {
                        return
                    }
                
                    do {
                        let result = try JSONDecoder().decode(YoloResponse.self, from: safeData)
                        
                        var Prediction = result.traffic_light
                        
                        if Prediction.contains("green")  {
                            Prediction = "green"
                        }
                        
                        MmWaveDataStore.shared.traffic_light = Prediction
                        print("回報號誌: \(result.traffic_light)")
                    } catch {
                        print("⚠️ JSON 解析失敗: \(error)")
                    }
                }
            }
        }
        task.resume()
    }
    
    func deleteFile(at url: URL) {
        try? FileManager.default.removeItem(at: url)
        print("🗑️ 暫存檔已刪除")
    }
}

