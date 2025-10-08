import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN, API_KEY
import os
import sqlite3
from datetime import datetime
from ai_service import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm import FSM, State


DB_PATH = "data/db.sqlite3"


class PracticeState(FSM):
    waiting_for_voice = State()

def ensure_db():
    dirpath = os.path.dirname(DB_PATH)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        registered_at TEXT,
        last_seen TEXT)""")
        conn.commit()

ensure_db()

def upsert_user(telegram_id: int, first_name: str, last_name: str, username:str):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
            INSERT INTO users(telegram_id, first_name, last_name, username, registered_at, last_seen)
             VALUES (?, ?, ?, ?, ?, ?)
            """, (telegram_id, first_name, last_name, username, now, now))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            cur.execute("""
            UPDATE users SET last_seen = ? WHERE telegram_id = ?""", (now, telegram_id))
            conn.commit()
            return False

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command('practice'))
async def practice_handler(message: Message, state: FSMContext):
    # Генерируем задание
    exercise_text = ai_service_exercise()
    # Создаем TTS для задания
    tts_bytes = tts_gtts_mp3_bytes(exercise_text)
    with open("tts.mp3", "wb") as f:
        f.write(tts_bytes)
    # Отправляем задание
    voice = FSInputFile("tts.mp3")
    await message.answer("Послушайте задание:")
    await message.answer_voice(voice)
    # Запрашиваем ответ пользователя
    await message.answer("Пожалуйста, ответьте голосом.")
    # Устанавливаем состояние ожидания голоса
    await state.set_state(PracticeState.waiting_for_voice)

@dp.message(PracticeState.waiting_for_voice)
async def handle_voice_response(message: Message, state: FSMContext):
    if not message.voice:
        await message.answer("Пожалуйста, отправьте голосовое сообщение.")
        return
    voice = message.voice
    # Скачиваем голосовое сообщение
    filename = "user_response.ogg"
    await voice.download(destination_file=filename)
    # Конвертируем OGG в WAV или MP3 при необходимости
    # Предположим, что transcribe_voice умеет работать с ogg
    user_text = transcribe_voice(filename)
    os.remove(filename)

    # Получаем обратную связь от AI
    feedback = ai_service(user_text)

    await message.answer(f"Ваш ответ: {user_text}")
    await message.answer(f"Обратная связь:\n{feedback}")

    # Сброс состояния
    await state.clear()




@dp.message(Command('help'))
async def help(message: Message):
   await message.answer("Этот бот умеет выполнять команды:\n/start \n/help \n/practice \n/support")

@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    user = message.from_user
    telegram_id = user.id
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    username = user.username or ""

    created = upsert_user(telegram_id, first_name, last_name, username)

    if created:
        await message.answer(
            f"Привет, {first_name}! Ты успешно зарегистрирован в SpeakSmart. "
            "Это базовый прототип на этапе 1."
        )
    else:
        await message.answer(
            f"Привет, {first_name}! Ты уже зарегистрирован в SpeakSmart."
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
