#ifndef SENSORS_H
#define SENSORS_H

#include <DHT.h>

struct SensorData {
    float temperature;
    float humidity;
    float ph;
    float ec;
    float waterLevel;
    bool pumpStatus[2];
};

class HydroponicSensors {
public:
    HydroponicSensors() : dht(DHT_PIN, DHT22) {
        dht.begin();
    }

    float readPH() {
        int rawValue = analogRead(PH_PIN);
        // Convert analog reading to pH value (needs calibration)
        float voltage = rawValue * (3.3 / 4095.0);
        return 7 + ((2.5 - voltage) / 0.18);
    }

    float readEC() {
        int rawValue = analogRead(EC_PIN);
        // Convert analog reading to EC value (needs calibration)
        float voltage = rawValue * (3.3 / 4095.0);
        return voltage * 1.0; // Placeholder conversion factor
    }

    float readTemperature() {
        return dht.readTemperature();
    }

    float readHumidity() {
        return dht.readHumidity();
    }

    float readWaterLevel() {
        digitalWrite(ULTRASONIC_TRIGGER, LOW);
        delayMicroseconds(2);
        digitalWrite(ULTRASONIC_TRIGGER, HIGH);
        delayMicroseconds(10);
        digitalWrite(ULTRASONIC_TRIGGER, LOW);

        long duration = pulseIn(ULTRASONIC_ECHO, HIGH);
        return duration * 0.034 / 2; // Distance in cm
    }

    SensorData readAll() {
        SensorData data;
        data.temperature = readTemperature();
        data.humidity = readHumidity();
        data.ph = readPH();
        data.ec = readEC();
        data.waterLevel = readWaterLevel();
        data.pumpStatus[0] = digitalRead(PUMP1_PIN);
        data.pumpStatus[1] = digitalRead(PUMP2_PIN);
        return data;
    }

private:
    DHT dht;
};

#endif
