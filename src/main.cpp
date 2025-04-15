#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "config.h"
#include "sensors.h"

WiFiClient espClient;
PubSubClient mqtt(espClient);
HydroponicSensors sensors;

unsigned long lastReadingTime = 0;
unsigned long lastPumpCheck = 0;
unsigned long lastIrrigationTime = 0;
bool isIrrigating = false;
unsigned long irrigationStartTime = 0;

const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -3 * 3600;  // GMT-3 for Brazil
const int daylightOffset_sec = 0;

void setupWiFi() {
    Serial.println("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
    while (!mqtt.connected()) {
        Serial.println("Attempting MQTT connection...");
        String clientId = "ESP32Client-";
        clientId += String(random(0xffff), HEX);
        
        if (mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
            Serial.println("Connected to MQTT");
            mqtt.subscribe(MQTT_BASE_TOPIC "control/#");
        } else {
            Serial.print("Failed, rc=");
            Serial.print(mqtt.state());
            Serial.println(" Retrying in 5 seconds");
            delay(5000);
        }
    }
}

void publishSensorData(const SensorData& data) {
    StaticJsonDocument<256> doc;
    
    doc["temperature"] = data.temperature;
    doc["humidity"] = data.humidity;
    doc["ph"] = data.ph;
    doc["ec"] = data.ec;
    doc["water_level"] = data.waterLevel;
    doc["pump1"] = data.pumpStatus[0];
    doc["pump2"] = data.pumpStatus[1];
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt.publish(MQTT_BASE_TOPIC "sensors", buffer);
}

void checkThresholds(const SensorData& data) {
    if (data.ph < PH_MIN || data.ph > PH_MAX) {
        mqtt.publish(MQTT_BASE_TOPIC "alerts", "pH fora do range ideal!");
    }
    if (data.ec < EC_MIN || data.ec > EC_MAX) {
        mqtt.publish(MQTT_BASE_TOPIC "alerts", "EC fora do range ideal!");
    }
    if (data.temperature < TEMP_MIN || data.temperature > TEMP_MAX) {
        mqtt.publish(MQTT_BASE_TOPIC "alerts", "Temperatura fora do range ideal!");
    }
    if (data.waterLevel < WATER_LEVEL_MIN) {
        mqtt.publish(MQTT_BASE_TOPIC "alerts", "Nível de água baixo!");
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    if (String(topic) == MQTT_BASE_TOPIC "control/pump1") {
        digitalWrite(PUMP1_PIN, message == "ON" ? HIGH : LOW);
    } else if (String(topic) == MQTT_BASE_TOPIC "control/pump2") {
        digitalWrite(PUMP2_PIN, message == "ON" ? HIGH : LOW);
    }
}

void setup() {
    Serial.begin(115200);
    
    // Setup pins
    pinMode(ULTRASONIC_TRIGGER, OUTPUT);
    pinMode(ULTRASONIC_ECHO, INPUT);
    pinMode(PUMP1_PIN, OUTPUT);
    pinMode(PUMP2_PIN, OUTPUT);
    pinMode(WATER_PUMP_PIN, OUTPUT);
    
    digitalWrite(PUMP1_PIN, LOW);
    digitalWrite(PUMP2_PIN, LOW);
    digitalWrite(WATER_PUMP_PIN, LOW);
    
    setupWiFi();
    
    // Initialize NTP
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
}

bool isNightMode() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return false;
    }
    
    int currentHour = timeinfo.tm_hour;
    return (currentHour >= NIGHT_MODE_START || currentHour < NIGHT_MODE_END);
}

void controlIrrigation(const SensorData& data) {
    unsigned long currentMillis = millis();
    
    // Check if we should stop ongoing irrigation
    if (isIrrigating && (currentMillis - irrigationStartTime >= IRRIGATION_DURATION)) {
        digitalWrite(WATER_PUMP_PIN, LOW);
        isIrrigating = false;
        mqtt.publish(MQTT_BASE_TOPIC "status", "Irrigation cycle completed");
        return;
    }
    
    // Don't start new irrigation if we're already irrigating
    if (isIrrigating) {
        return;
    }
    
    // Check if it's time for irrigation
    if (currentMillis - lastIrrigationTime >= IRRIGATION_INTERVAL) {
        // Don't irrigate during night mode
        if (isNightMode()) {
            mqtt.publish(MQTT_BASE_TOPIC "status", "Irrigation skipped - Night mode");
            return;
        }
        
        // Start irrigation cycle
        digitalWrite(WATER_PUMP_PIN, HIGH);
        isIrrigating = true;
        irrigationStartTime = currentMillis;
        lastIrrigationTime = currentMillis;
        mqtt.publish(MQTT_BASE_TOPIC "status", "Starting irrigation cycle");
        
        // Adjust nutrients if needed
        if (data.ec < EC_MIN) {
            digitalWrite(PUMP2_PIN, HIGH);
            delay(5000);  // Run nutrient pump for 5 seconds
            digitalWrite(PUMP2_PIN, LOW);
        }
        
        if (data.ph > PH_MAX) {
            digitalWrite(PUMP1_PIN, HIGH);
            delay(3000);  // Run pH down pump for 3 seconds
            digitalWrite(PUMP1_PIN, LOW);
        }
    }
}

void loop() {
    if (!mqtt.connected()) {
        reconnectMQTT();
    }
    mqtt.loop();
    
    unsigned long currentMillis = millis();
    
    // Read sensors every READING_INTERVAL
    if (currentMillis - lastReadingTime >= READING_INTERVAL) {
        lastReadingTime = currentMillis;
        
        SensorData data = sensors.readAll();
        publishSensorData(data);
        
        // Control irrigation based on sensor data
        controlIrrigation(data);
    }
    
    // Check pump status periodically
    if (currentMillis - lastPumpCheck >= PUMP_CHECK_INTERVAL) {
        lastPumpCheck = currentMillis;
        
        // Monitor water level
        SensorData data = sensors.readAll();
        if (data.waterLevel < WATER_LEVEL_MIN) {
            // Stop irrigation if water level is too low
            digitalWrite(WATER_PUMP_PIN, LOW);
            isIrrigating = false;
            mqtt.publish(MQTT_BASE_TOPIC "alerts", "Irrigation stopped - Low water level");
        }
    }
}
