import sqlite3
from config import *
from utils import hash_password

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Создаем таблицу пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    # Таблица истории измерений
    c.execute('''CREATE TABLE IF NOT EXISTS temperature_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL
    )''')
    
    # Очищаем таблицу истории
    c.execute("DELETE FROM temperature_history")

    # Добавляем тестового пользователя (admin/admin)
    hashed_pwd = hash_password("admin")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
             ("admin", hashed_pwd))
    
    conn.commit()
    conn.close()

def save_temperature_data(timestamp, temperature):
    """Сохранение данных о температуре"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO temperature_history 
                 (timestamp, temperature) 
                 VALUES (?, ?)''', 
              (timestamp, temperature))
    
    conn.commit()
    conn.close()

def get_temperature_history():
    """Получение истории изменений температуры"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Получаем последние 30 записей
    c.execute('''SELECT timestamp, temperature
                 FROM temperature_history 
                 ORDER BY timestamp DESC 
                 LIMIT 30''')
    
    history = [
        {
            'timestamp': row[0], 
            'temperature': row[1]
        } for row in c.fetchall()
    ]
    
    conn.close()
    return list(reversed(history))