import json
import os
from datetime import datetime
from collections import deque
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# Data storage (last 100 readings)
sensor_data = deque(maxlen=100)
status_messages = deque(maxlen=10)
alerts = deque(maxlen=10)

# Initialize Dash app
app = dash.Dash(__name__)

# Dashboard layout
app.layout = html.Div([
    html.H1('Hydroponics Monitoring Dashboard'),
    
    # Sensor Data Graphs
    html.Div([
        html.H2('Sensor Readings'),
        dcc.Graph(id='sensor-graph'),
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        ),
    ]),
    
    # Status and Alerts
    html.Div([
        html.Div([
            html.H3('System Status'),
            html.Div(id='status-messages')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3('Alerts'),
            html.Div(id='alerts')
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),
    
    # Manual Control
    html.Div([
        html.H2('Manual Control'),
        html.Button('Start Main Pump', id='btn-pump-main'),
        html.Button('Start pH Pump', id='btn-pump-ph'),
        html.Button('Start Nutrient Pump', id='btn-pump-nutrient'),
    ])
])

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to all hydroponics topics
    client.subscribe("hydroponics/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
        
        if topic == "hydroponics/sensors":
            payload['timestamp'] = datetime.now()
            sensor_data.append(payload)
        elif topic == "hydroponics/status":
            status_messages.append({
                'timestamp': datetime.now(),
                'message': payload
            })
        elif topic == "hydroponics/alerts":
            alerts.append({
                'timestamp': datetime.now(),
                'message': payload
            })
    except json.JSONDecodeError:
        print(f"Error decoding message from topic {topic}")

# Dash Callbacks
@app.callback(
    Output('sensor-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    if not sensor_data:
        return {}
    
    df = pd.DataFrame(list(sensor_data))
    
    return {
        'data': [
            {'x': df['timestamp'], 'y': df['temperature'], 'name': 'Temperature'},
            {'x': df['timestamp'], 'y': df['humidity'], 'name': 'Humidity'},
            {'x': df['timestamp'], 'y': df['ph'], 'name': 'pH'},
            {'x': df['timestamp'], 'y': df['ec'], 'name': 'EC'},
            {'x': df['timestamp'], 'y': df['water_level'], 'name': 'Water Level'}
        ],
        'layout': {
            'title': 'Sensor Readings Over Time',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Value'}
        }
    }

@app.callback(
    Output('status-messages', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_status(n):
    return [html.Div(f"{msg['timestamp'].strftime('%H:%M:%S')} - {msg['message']}") 
            for msg in list(status_messages)]

@app.callback(
    Output('alerts', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_alerts(n):
    return [html.Div(f"{alert['timestamp'].strftime('%H:%M:%S')} - {alert['message']}", 
                     style={'color': 'red'}) 
            for alert in list(alerts)]

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

if __name__ == '__main__':
    app.run_server(debug=True)
