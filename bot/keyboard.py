# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# def get_answer_keyboard():
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     answer_button = KeyboardButton(text="Ответить голосом", request_voice=True)
#     keyboard.add(answer_button)
#     return keyboard


from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем клавиатуру с кнопкой
def create_help_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_question")]
        ]
    )
    return keyboard

