import requests
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *
from database import save_temperature_data
from datetime import datetime
import requests
from utils import send_telegram_message

class TemperatureController:
    def __init__(self):
        self.current_temperature = None
        
    def check_temperature(self):
        """Проверка температуры и отправка уведомлений"""
        try:
            response = requests.get(f"{SENSOR_URL}/temperature")
            temp_data = response.json()
            self.current_temperature = temp_data['temperature']
            
            if self.current_temperature < -15:
                message = f"Температура {self.current_temperature}°C: Холодно! ❄️"
            elif -15 <= self.current_temperature <= 0:
                message = f"Температура {self.current_temperature}°C: Нейтрально. 🌬️"
            elif 0 < self.current_temperature < 15:
                message = f"Температура {self.current_temperature}°C: Скоро лето! 🌸"
            else:
                message = f"Температура {self.current_temperature}°C: Жарко! ☀️"

            print(message)

            # Сохраняем данные в БД
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_temperature_data(timestamp, self.current_temperature)

            send_telegram_message(message)
            
        except Exception as e:
            print(f"Ошибка мониторинга температуры: {e}")


if __name__ == "__main__":
    controller = TemperatureController()
    try:
        print("Контроллер запущен")
        while True:
            controller.check_temperature()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")