
# 🌱 Smart Weed Detection Rover

**AI-powered rover that detects weeds with YOLOv8 and auto-controls motors/LED/buzzer via ESP32.**

## ✨ Features
- Real-time weed detection (camera/video/image)
- ESP32 rover: **Weed → Chop ** | **No weed → Move **
- Streamlit dashboard with live feed, FPS, status
- False positive filtering (ignores environment parameters)

## 🛠 Quick Setup

### 1. Hardware
```
ESP8266 NodeMCU Pins:
- D1/D2: Left motors
- D3/D4: Right motors
- D5/D6: Blade motors
```
- WiFi: `"<your-ssid>"` / `"<password>"`

### 2. Software
```bash
# Install
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

### 3. Upload Firmware
- Arduino IDE → Upload `rover.ino`
- Note ESP IP from Serial Monitor

### 4. Configure
- `app.py`: Set `ESP_IP = "192.168.x.x"`

## 📱 Usage
1. Open [http://localhost:8501](http://localhost:8501)
2. Choose input: Live cam / Image / Video
3. **Green 🟢**: Weed → Chops the weed 
4. **Red 🔴**: Move → Motors move forward

**Test endpoints**:
```
http://ESP_IP/green  # Chop mode
http://ESP_IP/red    # Move mode
http://ESP_IP/status # Debug pins
```

## 📁 Structure
```
├── app.py       # Streamlit app
├── rover.ino    # ESP32 code
├── requirements.txt
└── README.md
```

## 🔧 Customize
- **More strict**: `conf=0.8` in `process_image()`
- **Motor speed**: `speedVal = 100`
- **WiFi**: Edit `ssid/password`

## 🐛 Issues
- **No ESP**: Check IP/Serial
- **Wrong lights**: Swap `HIGH/LOW` in `.ino`
- **False detections**: Tune `conf`/`min_area_pct`


***
