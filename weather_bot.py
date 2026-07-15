#!/usr/bin/env python3
import os
import sys
import datetime as dt
import requests
from PIL import Image, ImageDraw, ImageFont

# Координаты Костюковичей для прогноза погоды
LATITUDE = 53.3136
LONGITUDE = 32.0639

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_weather():
    """
    Получает актуальную погоду и прогноз на сегодня в Костюковичах через Open-Meteo API.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}"
        f"&longitude={LONGITUDE}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
        f"&wind_speed_unit=ms"
        f"&timezone=Europe/Minsk"
    )
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"🔴 Ошибка API погоды: Код {response.status_code}")
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
    return None

def get_weather_desc(code):
    """
    Декодирует WMO код погоды в понятное описание на русском языке.
    """
    wmo_codes = {
        0: ("Ясно", "☀️"),
        1: ("Преимущественно ясно", "🌤️"),
        2: ("Переменная облачность", "⛅"),
        3: ("Пасмурно", "☁️"),
        45: ("Туман", "🌫️"),
        48: ("Осаждающийся туман", "🌫️"),
        51: ("Легкая морось", "🌧️"),
        53: ("Умеренная морось", "🌧️"),
        55: ("Плотная морось", "🌧️"),
        61: ("Слабый дождь", "🌦️"),
        63: ("Умеренный дождь", "🌧️"),
        65: ("Сильный дождь", "🌧️"),
        71: ("Слабый снегопад", "🌨️"),
        73: ("Умеренный снегопад", "🌨️"),
        75: ("Сильный снегопад", "❄️"),
        77: ("Снежные зерна", "❄️"),
        80: ("Слабый ливень", "🌦️"),
        81: ("Умеренный ливень", "🌧️"),
        82: ("Сильный ливень", "⛈️"),
        85: ("Слабый снегопад (заряд)", "🌨️"),
        86: ("Сильный снегопад (заряд)", "❄️"),
