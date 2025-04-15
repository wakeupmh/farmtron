#ifndef CONFIG_H
#define CONFIG_H

// WiFi credentials
#define WIFI_SSID "your_ssid"
#define WIFI_PASSWORD "your_password"

// MQTT Configuration
#define MQTT_SERVER "your_mqtt_server"
#define MQTT_PORT 1883
#define MQTT_USER "your_mqtt_user"
#define MQTT_PASSWORD "your_mqtt_password"
#define MQTT_BASE_TOPIC "hydroponics/"

// Pins Configuration
#define DHT_PIN 4
#define PH_PIN 34
#define EC_PIN 35
#define ULTRASONIC_TRIGGER 5
#define ULTRASONIC_ECHO 18
#define PUMP1_PIN 19  // pH control pump
#define PUMP2_PIN 21  // EC/nutrient control pump
#define WATER_PUMP_PIN 22  // Main water pump for irrigation

// Sensor reading intervals
#define READING_INTERVAL 300000  // 5 minutes in milliseconds
#define PUMP_CHECK_INTERVAL 60000 // 1 minute in milliseconds

// Irrigation Control
#define IRRIGATION_INTERVAL 3600000  // 1 hour in milliseconds
#define IRRIGATION_DURATION 300000   // 5 minutes in milliseconds
#define NIGHT_MODE_START 20         // 8 PM
#define NIGHT_MODE_END 6           // 6 AM

// Thresholds
#define PH_MIN 5.5
#define PH_MAX 6.5
#define EC_MIN 1.5
#define EC_MAX 2.2
#define TEMP_MIN 20.0
#define TEMP_MAX 25.0
#define HUMIDITY_MIN 60.0
#define HUMIDITY_MAX 80.0
#define WATER_LEVEL_MIN 10.0  // cm from sensor

#endif
