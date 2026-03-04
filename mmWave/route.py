import os
import threading
from flask import Flask, request, jsonify
from ultralytics import YOLO


# 匯入剛剛建立的模組
import online_inference_gui

app = Flask(__name__)

mmwave_data = {
    "prediction": "Init...",
    "confidence": "Init..."
}

# 設定上傳與模型 (YOLO 建議在外面載入一次就好，效能會好很多)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

yolo_model = YOLO(r"best.pt")

@app.route('/get_mmwave', methods=['GET'])
def get_mmwave():
    return jsonify(mmwave_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']

    if file:

        debug_folder = r"uploads"

        full_path = os.path.join(debug_folder, file.filename)

        file.save(full_path)

        results = yolo_model.predict(full_path, device='cpu', save=False)

        traffic_light = "None"

        os.remove(full_path)

        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0]
            cls_id = int(box.cls[0])
            traffic_light = results[0].names[cls_id]
            traffic_light = traffic_light.capitalize()
        print(f"📸 YOLO 辨識: {traffic_light}")
        return jsonify({"traffic_light": traffic_light}), 200

    return jsonify({"error": "Failed"}), 400

if __name__ == '__main__':
    print("🚀 啟動背景執行緒 (毫米波)...")

    # 2. 啟動 Thread，並把 mmwave_data 傳進去給它寫
    t = threading.Thread(target=online_inference_gui.start_mmwave, args=(mmwave_data,))
    t.daemon = True # 設定為守護執行緒 (Flask 關掉時它也會關)
    t.start()

    print("🌐 Server 啟動中...")
    # use_reloader=False 避免執行緒跑兩次
    app.run(host='192.168.194.2', port=5000, debug=True, use_reloader=False)