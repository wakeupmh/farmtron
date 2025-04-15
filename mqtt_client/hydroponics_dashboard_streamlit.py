import os
import time
import threading
import queue
import pandas as pd
import streamlit as st
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from camera_client import IPCameraClient

load_dotenv()

# MQTT Config
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_SENSOR = os.getenv('MQTT_TOPIC_SENSOR', 'farmtron/sensor')
MQTT_TOPIC_STATUS = os.getenv('MQTT_TOPIC_STATUS', 'farmtron/status')
MQTT_TOPIC_ALERT = os.getenv('MQTT_TOPIC_ALERT', 'farmtron/alert')
MQTT_TOPIC_CONTROL = os.getenv('MQTT_TOPIC_CONTROL', 'farmtron/control')

# Camera config (optional)
CAMERA_URL = os.getenv('CAMERA_URL')
CAMERA_USER = os.getenv('CAMERA_USER')
CAMERA_PASS = os.getenv('CAMERA_PASS')

# Data queues
sensor_queue = queue.Queue(maxsize=100)
status_queue = queue.Queue(maxsize=10)
alert_queue = queue.Queue(maxsize=10)

# MQTT callbacks

def on_connect(client, userdata, flags, rc):
    client.subscribe([(MQTT_TOPIC_SENSOR, 0), (MQTT_TOPIC_STATUS, 0), (MQTT_TOPIC_ALERT, 0)])

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    if topic == MQTT_TOPIC_SENSOR:
        sensor_queue.put(payload)
    elif topic == MQTT_TOPIC_STATUS:
        status_queue.put(payload)
    elif topic == MQTT_TOPIC_ALERT:
        alert_queue.put(payload)

# MQTT client in background thread
def mqtt_thread():
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

mqtt_bg = threading.Thread(target=mqtt_thread, daemon=True)
mqtt_bg.start()

def get_latest_sensor_data():
    items = list(sensor_queue.queue)
    if not items:
        return pd.DataFrame()
    df = pd.DataFrame([eval(item) for item in items])
    return df

def get_latest_status():
    items = list(status_queue.queue)
    return '\n'.join(items[-5:])

def get_latest_alerts():
    items = list(alert_queue.queue)
    return '\n'.join(items[-5:])

def send_control_command(command):
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC_CONTROL, command)
    client.disconnect()

# Streamlit UI
st.set_page_config(page_title="Hydroponics Dashboard", layout="wide")
st.title("Hydroponics Monitoring Dashboard (Streamlit)")

# --- Camera Stream Section (Integrated from camera_streamlit.py) ---
st.sidebar.header("Camera Stream")
camera_url = st.sidebar.text_input("Camera Snapshot URL", value=os.getenv("CAMERA_URL", "http://CAMERA_IP:PORT/snapshot.jpg"))
username = st.sidebar.text_input("Camera Username (optional)", value=os.getenv("CAMERA_USER", ""))
password = st.sidebar.text_input("Camera Password (optional)", value=os.getenv("CAMERA_PASS", ""), type="password")
refresh_rate = st.sidebar.slider("Camera Refresh Interval (seconds)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)

if st.sidebar.button("Start Camera Stream"):
    camera = IPCameraClient(camera_url, username=username or None, password=password or None)
    frame_placeholder = st.empty()
    stop = st.sidebar.button("Stop Camera Stream")
    st.subheader("Live Camera Feed (Stream)")
    while not stop:
        try:
            image = camera.get_snapshot()
            frame_placeholder.image(image, channels="RGB")
        except Exception as e:
            frame_placeholder.warning(f"Camera error: {e}")
        time.sleep(refresh_rate)
else:
    st.info("Configure your camera in the sidebar and click 'Start Camera Stream' to view the live feed.")

# Sensor Data
st.subheader("Sensor Readings")
sensor_df = get_latest_sensor_data()
if not sensor_df.empty:
    st.line_chart(sensor_df)
else:
    st.info("Waiting for sensor data...")

# Status and Alerts
col1, col2 = st.columns(2)
with col1:
    st.subheader("System Status")
    st.text(get_latest_status() or "No status messages yet.")
with col2:
    st.subheader("Alerts")
    st.text(get_latest_alerts() or "No alerts yet.")

# Manual Control
st.subheader("Manual Control")
col1, col2 = st.columns(2)
if col1.button("Start Main Pump"):
    send_control_command("PUMP_MAIN_ON")
    st.success("Main pump command sent.")
if col2.button("Start pH Pump"):
    send_control_command("PUMP_PH_ON")
    st.success("pH pump command sent.")

st.caption("Farmtron - Hydroponics Automation & Monitoring | Streamlit Edition")
