# 🌱 Smart Hydroponics Monitoring & Automation System

An intelligent, secure, and modular hydroponics monitoring system using ESP32, Python dashboards, MQTT, and honeypot security measures. Designed for remote monitoring, automatic irrigation, and blue team (defensive) cybersecurity learning.

---

## 🚀 Project Overview

- **Embedded System (ESP32):** Collects sensor data (pH, EC, temperature, humidity, water level) and controls irrigation and nutrient pumps.
- **MQTT Communication:** Secure, real-time data exchange between embedded devices and dashboards.
- **Python Dashboard:** Visualizes data, allows manual control, and provides alerting.
- **Honeypots:** Multi-service honeypot system to detect and log unauthorized access attempts (FTP, MQTT, SSH, HTTP), protecting your real services.

---

## 📦 Hardware Components
- ESP32 DevKit
- pH Sensor (analog)
- Temperature and Humidity Sensor (DHT22)
- Electrical Conductivity Sensor (EC)
- Water Level Sensor (ultrasonic HC-SR04)
- 3 Pumps: Main Water, pH, Nutrients
- 4-Channel Relay Module
- Power Supply 5V/12V
- Jumper Wires and Breadboard

## ⚙️ Embedded System (`/embedded`)
- Written in C++ for ESP32 (see `/embedded/main.cpp`)
- Reads all sensors and controls pumps/relays
- Publishes sensor data and status to MQTT topics
- Receives control commands via MQTT
- Implements safety features: water level detection, night mode, auto-shutdown
- Fully configurable via `config.h`

### Main Features
- Automatic irrigation cycles (interval/duration configurable)
- Nutrient and pH adjustment during irrigation
- MQTT-based status/alert notifications
- Night mode (no irrigation at night)

## 📡 MQTT Topics
- `hydroponics/sensors` — Sensor data
- `hydroponics/status` — System and irrigation status
- `hydroponics/control` — Manual pump control
- `hydroponics/alerts` — System alerts

---

## 🛡️ Security & Honeypots (`/honeycomb`)
- Multi-service honeypot (FTP, MQTT, SSH, HTTP) to detect attackers
- Easy to run: `sudo python3 multi_honeypot_server.py`
- All events logged for blue team analysis
- Step-by-step router port forwarding instructions included

---

## 💻 Python Dashboard (`/mqtt_client`)
- Streamlit-based dashboard for real-time monitoring and manual control
- Connects securely to MQTT broker (supports AWS IoT Core)
- Sends alerts to Telegram on repeated failures
- Camera integration for live image capture (optional)

---

## 🛠️ Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/farmtron.git
   ```
2. **Configure the embedded system:**
   - Edit `/embedded/config.h` for WiFi, MQTT, and parameters
   - Upload to ESP32 using Arduino IDE or PlatformIO
3. **Run the honeypot (optional, for security):**
   - See `/honeycomb/README.md` for multi-honeypot setup and router config
4. **Run the dashboard:**
   - Configure `.env` in `/mqtt_client` (MQTT, Telegram, etc.)
   - Start with: `streamlit run hydroponics_dashboard_streamlit.py`

---

## 🔒 Security Best Practices
- Use VPN or TLS for MQTT communication
- Never expose real device admin interfaces to the internet
- Use honeypots to study and deter attackers
- Regularly update all firmware and software

---

## 📚 Technologies Used
- **Embedded:** Arduino (ESP32), PubSubClient (MQTT), ArduinoJson
- **Dashboard:** Python, Streamlit, paho-mqtt, pandas, python-dotenv
- **Security:** Custom Python honeypots, logging, Telegram alerts

---

## 🤖 For Blue Teamers & Learners
- Analyze honeypot logs to study real attacker behavior
- Expand honeypots for more protocols or richer interactions
- Integrate with SIEM or alerting systems

---

> This project is for educational, research, and defensive security purposes. Use responsibly!
