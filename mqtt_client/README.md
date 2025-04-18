# Hydroponics MQTT Dashboard

This is a real-time dashboard for monitoring your hydroponics system using MQTT data.

## Features

- Real-time sensor data visualization
- System status monitoring
- Alert notifications
- Manual pump control
- Historical data graphs

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MQTT connection:
```bash
cp .env.example .env
```
Edit the `.env` file with your MQTT broker details.

## Running the Dashboard

1. Make sure your hydroponics system is running and publishing to MQTT

2. Start the dashboard:
```bash
streamlit run hydroponics_dashboard_streamlit.py
```

3. Open your browser and navigate to:
```
http://localhost:8501
```

## Dashboard Features

### Real-time Monitoring
- Temperature
- Humidity
- pH levels
- EC (Electrical Conductivity)
- Water level

### System Status
- Current irrigation state
- Pump status
- System messages

### Alerts
- pH out of range
- EC out of range
- Water level warnings
- System errors

### Manual Control
- Control main water pump
- Control pH adjustment pump
- Control nutrient pump

## MQTT Topics

The dashboard subscribes to the following topics:

- `hydroponics/sensors` - Sensor data in JSON format
- `hydroponics/status` - System status messages
- `hydroponics/alerts` - System alerts and warnings
- `hydroponics/control` - Pump control commands

### Data Format Example

Sensor data JSON format:
```json
{
    "temperature": 23.5,
    "humidity": 65.0,
    "ph": 6.2,
    "ec": 1.8,
    "water_level": 15.0
}
```
