import hashlib
import secrets
import requests
from config import *

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")


def hash_password(password):
    """Безопасное хэширование пароля"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.sha512((password + salt).encode()).hexdigest()
    return f"{salt}${pwdhash}"

def verify_password(stored_password, provided_password):
    """Проверка пароля"""
    salt, pwdhash = stored_password.split('$')
    return pwdhash == hashlib.sha512((provided_password + salt).encode()).hexdigest()

def test():
    password = "123456"
    hashed_password = hash_password(password)
    print("Хешированный пароль: ", hashed_password)

    if verify_password(hashed_password, password):
        print("Пароль верен")
    else:
        print("Неверный пароль")

if __name__ == "__main__":
    test()