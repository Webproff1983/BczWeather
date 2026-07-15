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
        95: ("Гроза", "⛈️"),
        96: ("Гроза со слабым градом", "⛈️"),
        99: ("Гроза с сильным градом", "⛈️")
    }
    return wmo_codes.get(code, ("Облачно", "☁️"))

def download_font():
    """
    Скачивает красивый шрифт Montserrat Medium, если его нет локально.
    """
    font_path = "Montserrat-Medium.ttf"
    if not os.path.exists(font_path):
        print("Скачиваю красивый шрифт Montserrat...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Medium.ttf"
        try:
            r = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(r.content)
            print("Шрифт успешно сохранен!")
        except Exception as e:
            print(f"Не удалось скачать шрифт: {e}. Будет использован стандартный.")
            return None
    return font_path

def draw_weather_card(weather_data):
    """
    Накладывает красивую полупрозрачную плашку с погодой в правый нижний угол изображения БЦЗ.
    """
    background_path = "ChatGPT Image 14 июл. 2026 г., 21_48_45.png"

    output_path = "bcz_weather_output.png"
    
    if not os.path.exists(background_path):
        print(f"Ошибка: Не найден базовый фон {background_path}")
        return False
        
    # Открываем изображение завода
    img = Image.open(background_path).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Скачиваем/подключаем шрифт
    font_file = download_font()
    
    # Настройки размеров шрифтов (адаптируем под разрешение оригинального фото)
    # Исходное изображение широкое, поэтому шрифты делаем крупными
    if font_file:
        font_date = ImageFont.truetype(font_file, 40)
        font_temp = ImageFont.truetype(font_file, 100)
        font_desc = ImageFont.truetype(font_file, 35)
        font_sub = ImageFont.truetype(font_file, 28)
    else:
        # Резервный шрифт, если загрузка не удалась
        font_date = font_temp = font_desc = font_sub = ImageFont.load_default()
        
    # Парсим данные погоды
    curr = weather_data["current"]
    daily = weather_data["daily"]
    
    temp_now = round(curr["temperature_2m"])
    temp_min = round(daily["temperature_2m_min"][0])
    temp_max = round(daily["temperature_2m_max"][0])
    humidity = curr["relative_humidity_2m"]
    wind = curr["wind_speed_10m"]
    
    status_text, status_emoji = get_weather_desc(curr["weather_code"])
    
    # Формируем дату на русском языке
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    now_dt = dt.datetime.now()
    date_str = f"{weekdays[now_dt.weekday()]}, {now_dt.day} {months[now_dt.month - 1]}"
    
    # Рисуем стильную темную полупрозрачную плашку в правом нижнем углу
    # Координаты адаптированы под то, чтобы плашка красиво встала на фоне газона и скамейки
    width, height = img.size
    
    # Размер плашки
    p_width, p_height = 580, 420
    # Отступы от краев
    margin_right, margin_bottom = 80, 120
    
    x1 = width - p_width - margin_right
    y1 = height - p_height - margin_bottom
    x2 = width - margin_right
    y2 = height - margin_bottom
    
    # Черная плашка с прозрачностью 60% (150 из 255) и со скруглением углов
    draw.rounded_rectangle([x1, y1, x2, y2], radius=30, fill=(15, 23, 42, 160))
    
    # Наносим текст на плашку (смещение относительно левого верхнего угла плашки)
    draw.text((x1 + 40, y1 + 40), date_str.upper(), font=font_date, fill=(255, 255, 255, 255))
    
    # Отрисовка температуры
    sign = "+" if temp_now > 0 else ""
    temp_str = f"{sign}{temp_now}°C"
    draw.text((x1 + 40, y1 + 100), temp_str, font=font_temp, fill=(255, 255, 255, 255))
    
    # Отрисовка погоды (статус и эмодзи)
    draw.text((x1 + 40, y1 + 220), f"{status_emoji} {status_text}", font=font_desc, fill=(241, 245, 249, 255))
    
    # Прогноз на день и доп. параметры
    sign_min = "+" if temp_min > 0 else ""
    sign_max = "+" if temp_max > 0 else ""
    daily_str = f"Днем: {sign_max}{temp_max}° | Ночью: {sign_min}{temp_min}°"
    draw.text((x1 + 40, y1 + 290), daily_str, font=font_sub, fill=(203, 213, 225, 255))
    
    info_str = f"💨 Ветер: {wind} м/с  |  💧 Влажность: {humidity}%"
    draw.text((x1 + 40, y1 + 340), info_str, font=font_sub, fill=(203, 213, 225, 255))
    
    # Сохраняем готовую картинку
    final_img = img.convert("RGB")
    final_img.save(output_path, "JPEG", quality=90)
    print("Изображение погоды успешно сгенерировано!")
    return True

def send_telegram_card(weather_data):
    """
    Отправляет сгенерированную карточку в Telegram с текстовым описанием.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Настройки Telegram не заданы!")
        return False
        
    curr = weather_data["current"]
    daily = weather_data["daily"]
    status_text, status_emoji = get_weather_desc(curr["weather_code"])
    
    temp_now = round(curr["temperature_2m"])
    temp_min = round(daily["temperature_2m_min"][0])
    temp_max = round(daily["temperature_2m_max"][0])
    sign_now = "+" if temp_now > 0 else ""
    sign_min = "+" if temp_min > 0 else ""
    sign_max = "+" if temp_max > 0 else ""

    # Красивый сопроводительный текст для канала
    text = (
        f"☀️ <b>Доброе утро, коллеги!</b>\n\n"
        f"Информационная служба Белорусского цементного завода представляет прогноз погоды в Костюковичах на сегодня:\n\n"
        f"🌡 <b>Температура сейчас:</b> {sign_now}{temp_now}°C ({status_text} {status_emoji})\n"
        f"📈 <b>Днем воздух прогреется до:</b> {sign_max}{temp_max}°C\n"
        f"📉 <b>Ночью опустится до:</b> {sign_min}{temp_min}°C\n"
        f"💨 <b>Ветер:</b> {curr['wind_speed_10m']} м/с\n"
        f"💧 <b>Относительная влажность:</b> {curr['relative_humidity_2m']}%\n\n"
        f"Желаем вам продуктивного рабочего дня и отличного настроения! Твердость решений — уверенность в завтрашнем дне! 💪🏭"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    # Открываем созданную картинку и пушим в Telegram
    try:
        with open("bcz_weather_output.png", "rb") as photo:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": text,
                "parse_mode": "HTML"
            }
            files = {
                "photo": photo
            }
            response = requests.post(url, data=payload, files=files, timeout=30)
            if response.status_code == 200:
                print("Сообщение успешно опубликовано в канале!")
                return True
            else:
                print(f"Ошибка Telegram API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ошибка отправки фото в Telegram: {e}")
        
    return False

if __name__ == "__main__":
    print("Старт генератора утренней погоды БЦЗ...")
    weather = get_weather()
    if weather:
        if draw_weather_card(weather):
            send_telegram_card(weather)
    else:
        print("Не удалось запустить генерацию из-за сбоя API погоды.")
