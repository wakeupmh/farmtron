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

## Project Overview

Farmtron is an integrated system for hydroponics monitoring and automation, composed of:
- Embedded firmware (ESP32) responsible for sensor readings, pump control, and MQTT communication.
- A web dashboard (Python/Dash) for real-time data visualization, system status, and manual command sending.

## Architecture

- **Firmware (src/):**
  - Reads temperature, humidity, pH, and EC sensors.
  - Publishes periodic sensor readings via MQTT in JSON format.
  - Receives remote commands (e.g., pump activation) via MQTT topics.
  - Implements automatic irrigation logic, alert thresholds, and night mode.
- **Client/Dashboard (mqtt_client/):**
  - Receives and stores the latest readings and alerts.
  - Displays real-time graphs and system status (Dash).
  - Allows manual pump control through the web interface.

## Folder Structure

- `src/`
  - `main.cpp`: Main firmware logic.
  - `config.h`: System configurations (credentials, topics, thresholds, pins).
  - `sensors.h`: Abstraction for sensor reading.
- `mqtt_client/`
  - `hydroponics_dashboard.py`: Web dashboard in Python.
  - `requirements.txt`: Client dependencies.
  - `.env.example`: Example of required environment variables.

## How It Works

1. The ESP32 connects to WiFi, sets up NTP, sensors, and MQTT.
2. Periodically reads sensors and publishes data via MQTT.
3. The Python dashboard receives the data, stores it, and updates graphs and status.
4. Manual commands can be sent from the dashboard and reach the ESP32 via MQTT.
5. The firmware executes automatic irrigation and alert logic according to defined thresholds.

## Technologies Used
- **Firmware:** Arduino (ESP32), PubSubClient (MQTT), ArduinoJson
- **Dashboard:** Python, Dash, paho-mqtt, pandas, python-dotenv

## Highlights
- Modular and clearly separated firmware and client
- Robust MQTT communication
- Embedded automation with thresholds and night mode
- User-friendly web interface for monitoring and control

## Security: Best Practices for IP Camera Integration

To ensure the safety and privacy of your hydroponics monitoring system, follow these security recommendations when integrating IP cameras:

### Device-Level Security
- **Change Default Credentials:** Set strong, unique passwords for all camera accounts. Never use factory defaults.
- **Update Firmware:** Regularly update your camera’s firmware to patch vulnerabilities.
- **Disable Unused Services:** Turn off unnecessary services (FTP, Telnet, UPnP, etc.).
- **Limit User Accounts:** Use only the minimum accounts needed, with the lowest privilege necessary.

### Network Security
- **Network Segmentation:** Place cameras on a separate VLAN or subnet, isolated from your main network.
- **Firewall Rules:** Restrict camera access to trusted devices only. Block unnecessary inbound/outbound connections.
- **Avoid Port Forwarding:** Never expose camera ports directly to the internet. Use VPN or a secure reverse proxy if remote access is needed.
- **Prefer Wired Connections:** Use Ethernet instead of Wi-Fi when possible.

### Secure Communication
- **Enable HTTPS:** Always use HTTPS for camera web interfaces and streams if available.
- **Disable Insecure Protocols:** Turn off HTTP, Telnet, or other insecure protocols.

### Application-Level Security
- **Dashboard Authentication:** Protect your Streamlit/Dash dashboard with authentication so only authorized users can view camera feeds.
- **Secure Credential Storage:** Store camera URLs, usernames, and passwords in environment variables or encrypted config files. Never hardcode credentials.
- **Input Validation:** Validate and sanitize any user-supplied URLs or credentials in your app.

### Monitoring & Logging
- **Monitor Access Logs:** Regularly review logs for unauthorized access attempts.
- **Set Up Alerts:** Configure alerts for repeated failed logins or suspicious activity.

### Physical Security
- **Restrict Physical Access:** Secure the camera and networking equipment to prevent tampering.

### Summary Table

| Area             | Recommendation                                      |
|------------------|-----------------------------------------------------|
| Device           | Change defaults, update firmware, strong passwords  |
| Network          | VLAN, firewall, avoid port forwarding, wired if possible |
| Communication    | Use HTTPS, disable insecure protocols               |
| Application      | Dashboard auth, secure credential storage           |
| Monitoring       | Log and alert on suspicious activity                |
| Physical         | Secure installation location                        |

Following these best practices will help keep your system secure and your camera feeds private.

## 📚 Reference

This project is based on the article:
> [Design of a smart hydroponics monitoring system using an ESP32](https://www.sciencedirect.com/science/article/pii/S221501612303977)

## 📝 License

This project is under the MIT license.

## MQTT Reliability & Email Alerting

### MQTT Reconnection Logic
- The dashboard automatically attempts to reconnect to the MQTT broker if the connection is lost.
- All connection attempts, errors, and received MQTT messages are logged persistently to `dashboard.log` (or as set by the `DASHBOARD_LOG_FILE` environment variable).

### Persistent Logging
- Log file: `dashboard.log` (default, configurable via env).
- Logs include timestamps, log levels, connection events, errors, and MQTT messages.

### Email Alerts for Repeated Failures
- If the dashboard fails to connect to the MQTT broker repeatedly (default: 3 times), an alert email is sent to a configured address.
- Only one alert is sent per failure streak; after a successful connection, the counter resets.
- All email configuration is handled via environment variables for security and flexibility.

#### Environment Variables for Email Alerts
```
ALERT_EMAIL_TO=recipient@example.com         # Recipient email address
ALERT_EMAIL_FROM=dashboard@example.com       # Sender email address
ALERT_EMAIL_HOST=smtp.example.com           # SMTP server host
ALERT_EMAIL_PORT=587                        # SMTP server port (default 587)
ALERT_EMAIL_USER=dashboard@example.com       # SMTP username
ALERT_EMAIL_PASS=your_smtp_password         # SMTP password
ALERT_FAILURE_THRESHOLD=3                   # (Optional) Number of failures before alert (default 3)
```

### How to Configure a Free SMTP Server or Cloud Email Service

#### Gmail (Free for low volume, personal use)
1. Enable "Less secure app access" or create an App Password (recommended) in your Google Account.
2. Use the following settings:
   - `ALERT_EMAIL_HOST=smtp.gmail.com`
   - `ALERT_EMAIL_PORT=587`
   - `ALERT_EMAIL_USER=your_gmail@gmail.com`
   - `ALERT_EMAIL_PASS=your_app_password` (not your main account password)
3. Note: For production or higher reliability, use a dedicated email provider or domain.

#### Outlook/Hotmail (Free for personal use)
- `ALERT_EMAIL_HOST=smtp.office365.com`
- `ALERT_EMAIL_PORT=587`
- `ALERT_EMAIL_USER=your_email@outlook.com`
- `ALERT_EMAIL_PASS=your_password`

#### SendGrid (Free tier, suitable for cloud apps)
1. Sign up for a free SendGrid account: https://sendgrid.com/
2. Create an API key and enable SMTP relay.
3. Use the following settings:
   - `ALERT_EMAIL_HOST=smtp.sendgrid.net`
   - `ALERT_EMAIL_PORT=587`
   - `ALERT_EMAIL_USER=apikey` (literally the word "apikey")
   - `ALERT_EMAIL_PASS=your_sendgrid_api_key`

#### General Tips
- Always use app-specific passwords or API keys where possible.
- Never share your SMTP credentials publicly.
- For higher reliability, consider using a domain-based or transactional email provider.

With these features, Farmtron is robust against MQTT outages and provides real-time alerts for system reliability.
