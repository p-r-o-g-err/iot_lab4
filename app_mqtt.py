from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import paho.mqtt.client as mqtt
from config import *
from database import init_db, save_temperature_data, get_temperature_history
from utils import verify_password
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Глобальные переменные для хранения текущих данных
current_data = {
    'timestamp': None,
    'current_temperature': None
}

# Настройка MQTT клиента
mqtt_client = mqtt.Client("web_client")


def on_mqtt_message(client, userdata, msg):
    """Обработка входящих MQTT сообщений"""
    try:
        if msg.topic == MQTT_TOPIC_SENSOR:
            current_temperature = float(msg.payload.decode())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_data['current_temperature'] = current_temperature
            current_data['timestamp'] = timestamp
             # Сохраняем данные в базу при каждом новом измерении
            save_temperature_data(timestamp, current_temperature)
    except Exception as e:
        print(f"Ошибка обработки MQTT сообщения: {e}")

# Настройка MQTT подключения
def setup_mqtt():
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe([(MQTT_TOPIC_SENSOR, 0)])
    mqtt_client.loop_start()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Проверяем наличие специального флага формы
        if request.form.get('login_attempt') == 'true':
            username = request.form['username']
            password = request.form['password']
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username, password FROM users WHERE username = ?",
                    (username,))
            user = c.fetchone()
            conn.close()
            
            if user and verify_password(user[2], password):
                login_user(User(user[0], user[1]))
                return redirect(url_for('index'))
            flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/current_temperature')
@login_required
def current_temperature():
    """Получение текущих данных с сенсора"""
    return jsonify({
        'timestamp': current_data['timestamp'],
        'current_temperature': current_data['current_temperature']
    })

@app.route('/api/temperature_history')
@login_required
def temperature_history():
    """Получение истории измерений показаний"""
    history = get_temperature_history()
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    setup_mqtt()
    app.run(debug=True, use_reloader=False)  # use_reloader=False важно при использовании MQTT