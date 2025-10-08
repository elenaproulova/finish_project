import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN, API_KEY
import os
import sqlite3
from datetime import datetime

DB_PATH = "data/db.sqlite3"
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
