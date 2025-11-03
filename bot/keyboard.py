from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем клавиатуру с кнопкой
def create_help_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_question")]
        ]
    )
    return keyboard

