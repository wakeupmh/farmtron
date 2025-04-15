# Embedded Firmware for Smart Hydroponics

This directory contains the firmware for the ESP32-based hydroponics controller. It manages all sensors, pumps, relays, and communicates with the dashboard via MQTT for remote monitoring and automation.

---

## 🚀 Features
- Reads pH, EC, temperature, humidity, and water level sensors
- Controls irrigation, pH, and nutrient pumps via relays
- Automatic irrigation cycles with configurable interval/duration
- Nutrient and pH adjustment during irrigation
- MQTT-based communication for data, status, and alerts
- Night mode (prevents irrigation at night)
- Safety: auto-shutdown on low water, cycle timeout, and more

---

## 🛠️ Hardware Requirements
- ESP32 DevKit
- DHT22 (temperature/humidity)
- Analog pH sensor
- EC sensor
- Ultrasonic HC-SR04 (water level)
- 3 pumps (main, pH, nutrients)
- 4-channel relay module
- Power supply (5V/12V)
- Breadboard, jumper wires

### Wiring Diagram (GPIO Mapping)
```
ESP32 -----> Sensors and Actuators
- GPIO4  -> DHT22 (Temperature/Humidity)
- GPIO34 -> pH Sensor (Analog)
- GPIO35 -> EC Sensor
- GPIO5  -> HC-SR04 Trigger
- GPIO18 -> HC-SR04 Echo
- GPIO19 -> pH Pump Relay
- GPIO21 -> Nutrient Pump Relay
- GPIO22 -> Main Pump Relay
```

---

## 📂 File Structure
- `main.cpp`   — Main control logic, MQTT, automation
- `config.h`   — WiFi, MQTT, thresholds, GPIOs, timings
- `sensors.h`  — Sensor abstraction and reading

---

## ⚙️ Configuration
Edit `config.h` before uploading:
- **WiFi:** `WIFI_SSID`, `WIFI_PASSWORD`
- **MQTT:** `MQTT_SERVER`, `MQTT_PORT`, `MQTT_USER`, `MQTT_PASSWORD`, topics
- **Thresholds:** pH, EC, temperature, humidity, water level
- **GPIOs:** Pin assignments for each sensor/relay
- **Irrigation:** Interval, duration, night mode hours

---

## 📝 How It Works
1. On boot: connects to WiFi, syncs time (NTP), connects to MQTT
2. Periodically reads all sensors
3. Publishes sensor data to MQTT
4. Checks if irrigation is needed (interval, night mode)
5. During irrigation:
   - Activates main pump
   - Checks EC/pH and doses nutrients/pH as needed
   - Monitors water level and timeouts for safety
6. Receives manual control or config commands via MQTT
7. Publishes status and alerts (low water, errors, etc.)

---

## 📡 MQTT Topics
- `hydroponics/sensors` — Publishes JSON with all sensor data
- `hydroponics/status` — Publishes system and irrigation status
- `hydroponics/control` — Receives manual pump/relay commands
- `hydroponics/alerts` — Publishes alerts (low water, errors)

### Example Sensor Data (JSON)
```json
{
  "temp": 23.5,
  "humidity": 70,
  "ph": 6.1,
  "ec": 1.8,
  "water_level": 15,
  "timestamp": "2025-04-15T01:00:00Z"
}
```

---

## 🛠️ Building & Uploading
### Arduino IDE
1. Install ESP32 board support ([instructions](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html))
2. Install required libraries: DHT sensor, PubSubClient, ArduinoJson
3. Open `main.cpp` and configure `config.h`
4. Select ESP32 board and correct port
5. Upload to your device

### PlatformIO
1. Install PlatformIO in VSCode
2. Open `/embedded` as a project
3. Edit `platformio.ini` as needed
4. Configure `config.h`
5. Build and upload

---

## 🛡️ Safety Features
- Automatic shutdown if water level is too low
- Night mode: disables irrigation between set hours
- Cycle timeout: ensures pumps do not run indefinitely
- MQTT alerts for all critical events

---

## 🐞 Troubleshooting
- **WiFi not connecting:** Check SSID/password, move closer to router
- **No MQTT:** Check broker address, port, credentials, network
- **Sensors not reading:** Check wiring, pin assignments in `config.h`
- **No irrigation:** Check water level, relay wiring, pump power
- **Debugging:** Use serial monitor (115200 baud) for logs

---

## 📚 References
- Based on [Design of a smart hydroponics monitoring system using an ESP32](https://www.sciencedirect.com/science/article/pii/S221501612303977)

---

> For educational and research use. Always test safety features before deploying unattended!
