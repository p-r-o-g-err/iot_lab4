from flask import Flask, jsonify
import threading
import math

app_sensor = Flask(__name__)

class TemperatureSensor:
    def __init__(self):
        self.current_temperature  = 0
        self.time_step = 0  # Время для симуляции, будет увеличиваться с каждым вызовом simulate

    def simulate(self):
        # Симуляция изменения температуры
        # Используем косинусоиду для изменения температуры
        amplitude = 20  # Амплитуда колебаний (максимальная температура отклонения от среднего)
        frequency = 0.3  # Частота колебаний (сколько раз в единицу времени температура изменяется)
        
        # Косинусная волна, которая изменяет температуру с течением времени
        self.current_temperature = amplitude * math.cos(frequency * self.time_step)
        
        # Увеличиваем шаг времени для следующего вызова
        self.time_step += 1
        
        # self.current_temperature  += random.uniform(-1, 1)
        # Ограничиваем температуру в пределах диапазона от -40 до 40 градусов
        self.current_temperature  = max(-40, min(40, self.current_temperature ))
        return round(self.current_temperature , 1)

@app_sensor.route('/temperature', methods=['GET'])
def get_temperature():
    global sensor
    return jsonify({
        'temperature': sensor.simulate()
    })

def run_sensor_app():
    app_sensor.run(port=5001)

if __name__ == "__main__":
    sensor = TemperatureSensor()
    
    # Запуск серверов в отдельных потоках
    sensor_thread = threading.Thread(target=run_sensor_app)
    sensor_thread.start()

    sensor_thread.join()
    print("Запущены симуляторы устройств")