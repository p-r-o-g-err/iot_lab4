import time
import paho.mqtt.client as mqtt
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *
import math

class TemperatureSensor:
    """Симулятор датчика температуры"""
    def __init__(self):
        self.client = mqtt.Client("temperature_sensor")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)

        self.current_temperature  = 0
        self.time_step = 0  # Время для симуляции, будет увеличиваться с каждым вызовом simulate
        self.client.loop_start()

    def simulate(self):
        """Одно измерение температуры"""
        amplitude = 20
        frequency = 0.3
        self.current_temperature = amplitude * math.cos(frequency * self.time_step)
        self.time_step += 1
        self.current_temperature  = max(-40, min(40, self.current_temperature ))
        # Публикация значения температуры
        self.client.publish(MQTT_TOPIC_SENSOR, f"{self.current_temperature:.1f}")
        print(f"Текущая температура: {self.current_temperature:.1f}°C")
        # time.sleep(2)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

def run_sensor(sensor):
    try:
        print("Запуск симуляции датчика влажности")
        while True:
            sensor.simulate()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nОстановка симуляции датчика влажности")
        sensor.stop()

if __name__ == "__main__":
    sensor = TemperatureSensor()
    sensor_thread = threading.Thread(target=run_sensor, args=(sensor,))
    sensor_thread.start()
    try:
        sensor_thread.join()
    except KeyboardInterrupt:
        print("\nОстановка симуляции")