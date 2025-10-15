from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_answer_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    answer_button = KeyboardButton(text="Ответить голосом", request_voice=True)
    keyboard.add(answer_button)
    return keyboard

