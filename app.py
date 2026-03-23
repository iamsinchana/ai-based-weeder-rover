import cv2
import time
import numpy as np
import streamlit as st
from ultralytics import YOLO
import requests

# Load YOLO model
model = YOLO("weed-rover.pt")

# IP address
ESP_IP = "192.168.90.253"

def send_esp_command(color):
    try:
        if color == "green":
            requests.get(f"http://{ESP_IP}/green", timeout=0.5)
        else:
            requests.get(f"http://{ESP_IP}/red", timeout=0.5)
    except requests.exceptions.RequestException:
        print("Unable to reach ESP device.")

st.set_page_config(page_title="Smart Weed Detection", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp, .main { background-color: #121212; color: white; }
    h1, h2, h3 { color: #1de9b6; text-align: center; font-weight: 700; }
    .paragraph { color: #cccccc; font-size: 1.1rem; line-height: 1.6; }
    .light-green { font-size: 4rem; text-align: center; animation: glowG 1s infinite alternate; }
    .light-red { font-size: 4rem; text-align: center; animation: glowR 1s infinite alternate; }
    @keyframes glowG { from {text-shadow: 0 0 5px #00ff00;} to {text-shadow: 0 0 25px #00ff00;} }
    @keyframes glowR { from {text-shadow: 0 0 5px #ff0000;} to {text-shadow: 0 0 25px #ff0000;} }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Smart Weed Detection Rover Dashboard")

left, right = st.columns([2, 1])

with right:
    st.subheader("📘 Project Overview")
    st.markdown("""
    <div class="paragraph">
    Detects **weeds only** (ignores humans/environment).  
    Weed → 🟢 CUT | No weed → 🔴 MOVE
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("⚙ Input Source")
    source = st.radio("Choose input type:", ["Live Camera", "Upload Image", "Upload Video"])

with left:
    st.subheader("📡 Live Detection Feed")
    frame_box = st.empty()
    light_box = st.empty()
    fps_box = st.empty()
    confidence_box = st.empty()

def process_image(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = image.shape[:2]
    min_area_pct = 0.015  # Min 1.5% area (weeds not tiny)
    
    # FIXED: High conf, low NMS overlap, few max dets
    results = model(img_rgb, conf=0.75, iou=0.6, max_det=3)
    
    weed_detected = False
    conf_value = 0
    
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                c = box.conf[0].item()
                conf_value = max(conf_value, round(c * 100, 1))
                
                # Box size filter
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                area = (x2 - x1) * (y2 - y1)
                if area > min_area_pct * w * h:
                    weed_detected = True
                    break
    
    annotated = results[0].plot()
    return annotated, weed_detected, conf_value

if source == "Live Camera":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Could not open camera.")
        st.stop()
    
    prev_time = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        start = time.time()
        annotated, weed_detected, conf_val = process_image(frame)
        end = time.time()
        
        fps = round(1 / (end - start), 1)
        
        frame_box.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", width=640)
        fps_box.markdown(f"### ⚡ FPS: **{fps}**")
        confidence_box.markdown(f"### 📊 Confidence: **{conf_val}%**")
        
        if weed_detected:
            light_box.markdown("<div class='light-green'>🟢 WEED</div>", unsafe_allow_html=True)
            send_esp_command("green")
        else:
            light_box.markdown("<div class='light-red'>🔴 MOVE</div>", unsafe_allow_html=True)
            send_esp_command("red")
        
        time.sleep(0.03)

elif source == "Upload Image":
    uploaded = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])
    if uploaded:
        file_bytes = np.frombuffer(uploaded.read(), np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        annotated, weed_detected, conf_val = process_image(img)
        
        frame_box.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", width=640)
        confidence_box.markdown(f"### 📊 Confidence: **{conf_val}%**")
        
        if weed_detected:
            light_box.markdown("<div class='light-green'>🟢 WEED</div>", unsafe_allow_html=True)
            send_esp_command("green")
        else:
            light_box.markdown("<div class='light-red'>🔴 MOVE</div>", unsafe_allow_html=True)
            send_esp_command("red")

elif source == "Upload Video":
    uploaded = st.file_uploader("Upload a Video", type=["mp4", "avi", "mov"])
    if uploaded:
        tfile = "temp_video.mp4"
        with open(tfile, "wb") as f:
            f.write(uploaded.read())
        
        cap = cv2.VideoCapture(tfile)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            start = time.time()
            annotated, weed_detected, conf_val = process_image(frame)
            end = time.time()
            
            fps = round(1 / (end - start), 1)
            
            frame_box.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", width=640)
            fps_box.markdown(f"### ⚡ FPS: **{fps}**")
            confidence_box.markdown(f"### 📊 Confidence: **{conf_val}%**")
            
            if weed_detected:
                light_box.markdown("<div class='light-green'>🟢 WEED</div>", unsafe_allow_html=True)
                send_esp_command("green")
            else:
                light_box.markdown("<div class='light-red'>🔴 MOVE</div>", unsafe_allow_html=True)
                send_esp_command("red")
            
            time.sleep(0.03)
        cap.release()
