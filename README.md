# 🌱 Smart Hydroponics Monitoring System

An intelligent hydroponic monitoring system using ESP32. The system collects environmental data and nutrients for remote monitoring and automatic irrigation control.

## 📦 Hardware Components

- ESP32 DevKit
- pH Sensor (analog)
- Temperature and Humidity Sensor (DHT22)
- Electrical Conductivity Sensor (EC)
- Water Level Sensor (ultrasonic HC-SR04)
- 3 Pumps:
  - Main Water Pump (irrigation)
  - Peristaltic Pump for pH
  - Peristaltic Pump for nutrients
- 4-Channel Relay Module
- Power Supply 5V/12V
- Jumper Wires and Breadboard

## ⚙️ Connection Diagram

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

## 🌊 Automatic Irrigation System

### Irrigation Cycles
- **Interval**: Every 1 hour (configurable via `IRRIGATION_INTERVAL`)
- **Duration**: 5 minutes per cycle (configurable via `IRRIGATION_DURATION`)
- **Night Mode**: System pauses irrigation between 8 PM and 6 AM

### Nutrient Control
During each irrigation cycle, the system:
1. Checks EC and pH levels
2. If EC is low:
   - Activates nutrient pump for 5 seconds
3. If pH is high:
   - Activates pH pump for 3 seconds

### Safety Features
- Continuous water level monitoring
- Automatic shutdown if water level is low
- Night mode to prevent irrigation during inappropriate hours
- Automatic shutdown after irrigation cycle
- Status notifications via MQTT

## 💻 Software

### Dependencies

```bash
# Required Arduino Libraries:
- DHT sensor library
- PubSubClient (MQTT)
- ArduinoJson
- Time (NTP)
```

### Project Structure

```
/src
  ├── main.cpp          # Main code and irrigation control
  ├── config.h          # System settings and parameters
  └── sensors.h         # Sensor interfaces
```

## 📊 System Parameters

### Irrigation
- Cycle interval: 1 hour
- Cycle duration: 5 minutes
- Night hours: 8 PM to 6 AM

### Control Limits
- pH: 5.5 - 6.5
- EC: 1.5 - 2.2 mS/cm
- Temperature: 20°C - 25°C
- Humidity: 60% - 80%
- Minimum water level: 10cm

## 📡 MQTT Topics

- `hydroponics/sensors` - Sensor data
- `hydroponics/status` - System and irrigation status
- `hydroponics/control` - Manual pump control
- `hydroponics/alerts` - System alerts

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/farmtron.git
```

2. Configure `config.h`:
   - WiFi credentials
   - MQTT server
   - Adjust irrigation parameters if needed

3. Install dependencies in Arduino IDE or PlatformIO

4. Upload the code to ESP32

## ⚡ Operation

1. **Initialization**:
   - WiFi connection
   - NTP synchronization for time control
   - MQTT broker connection

2. **Main Cycle**:
   - Sensor readings every 5 minutes
   - Irrigation cycle check every hour
   - Continuous water level monitoring

3. **Irrigation Control**:
   - Checks time (avoids night irrigation)
   - Activates main pump
   - Adjusts nutrients if needed
   - Monitors cycle time
   - Automatically shuts down after 5 minutes

4. **Safety**:
   - Checks water level before irrigation
   - Monitors pH and EC values
   - MQTT alert system

## 📚 Reference

This project is based on the article:
> [Design of a smart hydroponics monitoring system using an ESP32](https://www.sciencedirect.com/science/article/pii/S221501612303977)

## 📝 License

This project is under the MIT license.
