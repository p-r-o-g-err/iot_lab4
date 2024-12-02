import paho.mqtt.client as mqtt
import sqlite3
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *
from utils import send_telegram_message

class TemperatureController:
    def __init__(self):
        self.client = mqtt.Client("temperature_controller")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        
        # Подписываемся на топик с данными датчика
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_SENSOR)
        
        self.current_temperature = None
        self.client.loop_start()
    
    def on_message(self, client, userdata, msg):
        """Обработка входящих сообщений"""
        try:
            if msg.topic == MQTT_TOPIC_SENSOR:
                # Получили новые данные от датчика
                self.current_temperature = float(msg.payload.decode())
                self.check_temperature()
                
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
    
    def check_temperature(self):
        """Проверка температуры и отправка уведомлений"""
        if self.current_temperature is None:
            return
             
        if self.current_temperature < -15:
            message = f"Температура {self.current_temperature}°C: Холодно! ❄️"
        elif -15 <= self.current_temperature <= 0:
            message = f"Температура {self.current_temperature}°C: Нейтрально. 🌬️"
        elif 0 < self.current_temperature < 15:
            message = f"Температура {self.current_temperature}°C: Скоро лето! 🌸"
        else:
            message = f"Температура {self.current_temperature}°C: Жарко! ☀️"

        print(message)
        send_telegram_message(message)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    controller = TemperatureController()
    try:
        print("Контроллер запущен")
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")
    finally:
        controller.stop()