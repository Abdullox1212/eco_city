from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_contact_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)
    keyboard.add(button)
    return keyboard

def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="♻️ Chiqindilarni tozalash xizmati"), KeyboardButton(text="🌱 O'simliklarga buyurtma berish"))
    return keyboard

def tanlov():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="📍 Lokatsiya yuboraman"), KeyboardButton(text="✍️ Matn yuboraman"))
    return keyboard

def order_plant_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="Ha"), KeyboardButton(text="Yo'q"))
    return keyboard


def go_site():  
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="🛍️ Saytga o'tish", url="https://youtube.com")
    keyboard.add(button1)
    return keyboard