import os
import time
import threading
import queue
import pandas as pd
import streamlit as st
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from camera_client import IPCameraClient
import json
import logging
import requests


load_dotenv()

# Persistent logging setup
LOG_FILE = os.getenv('DASHBOARD_LOG_FILE', 'dashboard.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("farmtron_dashboard")

# Log dashboard start
logger.info("Hydroponics dashboard started.")

# MQTT Config
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_TOPIC_SENSOR = os.getenv('MQTT_TOPIC_SENSOR', 'hydroponics/sensors')
MQTT_TOPIC_STATUS = os.getenv('MQTT_TOPIC_STATUS', 'hydroponics/status')
MQTT_TOPIC_ALERT = os.getenv('MQTT_TOPIC_ALERT', 'hydroponics/alerts')
MQTT_TOPIC_CONTROL = os.getenv('MQTT_TOPIC_CONTROL', 'hydroponics/control')

# Camera config (optional)
CAMERA_URL = os.getenv('CAMERA_URL')
CAMERA_USER = os.getenv('CAMERA_USER')
CAMERA_PASS = os.getenv('CAMERA_PASS')

# Telegram Alert Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ALERT_FAILURE_THRESHOLD = int(os.getenv('ALERT_FAILURE_THRESHOLD', 3))

# Data queues
sensor_queue = queue.Queue(maxsize=100)
status_queue = queue.Queue(maxsize=10)
alert_queue = queue.Queue(maxsize=10)

# Publisher client for control messages
publish_client = mqtt.Client()
if MQTT_USER and MQTT_PASSWORD:
    publish_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
publish_client.connect(MQTT_BROKER, MQTT_PORT, 60)
publish_client.loop_start()

# MQTT callbacks (with logging)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker.")
        client.subscribe([(MQTT_TOPIC_SENSOR, 0), (MQTT_TOPIC_STATUS, 0), (MQTT_TOPIC_ALERT, 0)])
    else:
        logger.error(f"MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    logger.info(f"Received MQTT message on {topic}: {payload}")
    if topic == MQTT_TOPIC_SENSOR:
        sensor_queue.put(payload)
    elif topic == MQTT_TOPIC_STATUS:
        status_queue.put(payload)
    elif topic == MQTT_TOPIC_ALERT:
        alert_queue.put(payload)

# Telegram Alert Function
def send_failure_alert_telegram(error_msg):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram alert config incomplete; cannot send alert.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    text = f"🚨 Farmtron ALERT: Repeated MQTT connection failures!\n\nLast error: {error_msg}"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Sent MQTT failure alert to Telegram chat {TELEGRAM_CHAT_ID}")
        else:
            logger.error(f"Failed to send Telegram alert: {resp.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")

# MQTT client in background thread with reconnection logic and Telegram alerts
def mqtt_thread():
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    failure_count = 0
    alert_sent = False
    while True:
        try:
            logger.info("Connecting to MQTT broker...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
            failure_count = 0
            alert_sent = False
        except Exception as e:
            logger.error(f"MQTT connection error: {e}. Retrying in 5 seconds...")
            failure_count += 1
            if failure_count >= ALERT_FAILURE_THRESHOLD and not alert_sent:
                send_failure_alert_telegram(str(e))
                alert_sent = True
            time.sleep(5)

mqtt_bg = threading.Thread(target=mqtt_thread, daemon=True)
mqtt_bg.start()

@st.cache_data(ttl=1)
def get_latest_sensor_data():
    data = []
    while True:
        try:
            raw = sensor_queue.get_nowait()
            data.append(json.loads(raw))
        except queue.Empty:
            break
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def get_latest_status():
    data = []
    while True:
        try:
            data.append(status_queue.get_nowait())
        except queue.Empty:
            break
    return '\n'.join(data[-5:])

def get_latest_alerts():
    data = []
    while True:
        try:
            data.append(alert_queue.get_nowait())
        except queue.Empty:
            break
    return '\n'.join(data[-5:])

def send_control_command(command):
    publish_client.publish(MQTT_TOPIC_CONTROL, command)

# Streamlit UI
st.set_page_config(page_title="Hydroponics Dashboard", layout="wide")
st.title("Hydroponics Monitoring Dashboard (Streamlit)")

# --- Camera Stream Section (Improved) ---
with st.sidebar.expander("Camera Stream", expanded=True):
    camera_url = st.text_input("Camera Snapshot URL", value=os.getenv("CAMERA_URL", "http://CAMERA_IP:PORT/snapshot.jpg"))
    username = st.text_input("Camera Username (optional)", value=os.getenv("CAMERA_USER", ""))
    password = st.text_input("Camera Password (optional)", value=os.getenv("CAMERA_PASS", ""), type="password")
    refresh_rate = st.slider("Camera Refresh Interval (seconds)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
    start_stream = st.button("Start Camera Stream")
    stop_stream = st.button("Stop Camera Stream")

if 'streaming' not in st.session_state:
    st.session_state['streaming'] = False
if start_stream:
    st.session_state['streaming'] = True
if stop_stream:
    st.session_state['streaming'] = False

if st.session_state['streaming']:
    st.subheader("Live Camera Feed (Stream)")
    camera = IPCameraClient(camera_url, username=username or None, password=password or None)
    frame_placeholder = st.empty()
    while st.session_state['streaming']:
        try:
            image = camera.get_snapshot()
            frame_placeholder.image(image, channels="RGB")
        except Exception as e:
            frame_placeholder.warning(f"Camera error: {e}")
        time.sleep(refresh_rate)
        st.experimental_rerun()
else:
    st.info("Configure your camera in the sidebar and click 'Start Camera Stream' to view the live feed.")

# --- Sensor Data Section ---
st.subheader("Sensor Readings")
# Warn if queue is near capacity
if sensor_queue.full():
    st.warning("Sensor queue is full; data may be lost.")
try:
    sensor_df = get_latest_sensor_data()
except Exception as e:
    st.error(f"Error parsing sensor data: {e}")
    sensor_df = pd.DataFrame()
if not sensor_df.empty:
    st.line_chart(sensor_df)
else:
    st.info("Waiting for sensor data...")

# --- Status and Alerts Section ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("System Status")
    st.text(get_latest_status() or "No status messages yet.")
with col2:
    st.subheader("Alerts")
    st.text(get_latest_alerts() or "No alerts yet.")

# --- Manual Control Section ---
st.subheader("Manual Control")
col1, col2 = st.columns(2)
if col1.button("Start Main Pump"):
    send_control_command("PUMP_MAIN_ON")
    st.success("Main pump command sent.")
if col2.button("Start pH Pump"):
    send_control_command("PUMP_PH_ON")
    st.success("pH pump command sent.")

st.caption("Farmtron - Hydroponics Automation & Monitoring | Streamlit Edition")
