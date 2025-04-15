# Honeycomb Multi-Service Honeypot for Blue Team

This directory contains honeypots for multiple popular services (FTP, MQTT, SSH, HTTP) to help you detect, log, and study intrusion attempts on your network. Perfect for blue team training and IoT defense!

## What’s included?
- **multi_honeypot_server.py**: Runs fake FTP, MQTT, SSH, and HTTP servers simultaneously.
- **honeycomb_server.py**: (Legacy) Standalone FTP honeypot.

## Simulated Services & Ports
| Service | Port   | Description                   |
|---------|--------|-------------------------------|
| FTP     | 2121   | Fake FTP server               |
| MQTT    | 1883   | Fake MQTT broker              |
| SSH     | 22     | Fake SSH banner/prompt        |
| HTTP    | 80     | Fake IoT admin web interface  |

All honeypots log connections, credentials, and suspicious activity to `honeycomb_multi.log`.

## Step-by-step: How to Run the Multi-Honeypot

1. **Install Python 3.x**
   - On Raspberry Pi/Ubuntu: `sudo apt update && sudo apt install python3`
   - On Windows: [Download Python](https://www.python.org/downloads/)

2. **Open a terminal (or command prompt) on your honeypot device.**

3. **Navigate to the honeycomb directory:**
   ```bash
   cd /path/to/farmtron/honeycomb
   ```

4. **Run the multi-honeypot script:**
   ```bash
   sudo python3 multi_honeypot_server.py
   ```
   - `sudo` is required for ports 22 (SSH) and 80 (HTTP) on Linux.
   - On Windows, run as administrator if needed.

5. **Check that it’s running:**
   - You should see a message like:
     ```
     Honeycomb multi-honeypot running! (FTP:2121, MQTT:1883, SSH:22, HTTP:80)
     Logs at: honeycomb_multi.log
     ```

6. **View logs:**
   - All activity is logged in `honeycomb_multi.log` in the same directory.
   - Use `tail -f honeycomb_multi.log` (Linux) to watch logs live.

7. **(Optional) Set up to run on boot:**
   - Use `tmux`, `screen`, or a systemd service to keep the honeypot running in the background.

## How to configure your router (port forwarding)
1. **Find your honeypot device’s local IP address** (e.g., `192.168.1.50`).
2. **Access your router’s admin page** and locate Port Forwarding/NAT settings.
3. **Forward these external ports to your honeypot’s internal IP:**
   - **21 → 2121** (FTP)
   - **22 → 22**   (SSH)
   - **80 → 80**   (HTTP)
   - **1883 → 1883** (MQTT)
   - (You can forward only the ports you want to monitor)
4. **Save and test:** Try connecting from outside your network and check the log file for activity.

## Security notes
- Use only in a lab or controlled environment.
- Never expose real services or sensitive data.
- Monitor logs regularly for suspicious activity.
- This does NOT replace a real firewall or security best practices.

## Blue Team Tips
- Analyze logs to study attacker behavior and techniques.
- Integrate with alerting (Telegram, email, etc.) for real-time notifications.
- Expand honeypots to simulate more protocols or richer fake interactions.

---
> **This honeypot is for educational and blue team (defensive) cybersecurity learning. Use responsibly!**
