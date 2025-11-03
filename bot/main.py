import asyncio
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, FSInputFile
from config import TOKEN, API_KEY
import sqlite3
from datetime import datetime
from ai_service import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from transcrib_voice import *
from keyboard import create_help_keyboard


DB_PATH = "data/db.sqlite3"
MANAGER_CHAT_ID = 404791943

class PracticeState(StatesGroup):
    waiting_for_voice = State()

class AskQuestion(StatesGroup):
    waiting_for_question = State()

def ensure_db():
    dirpath = os.path.dirname(DB_PATH)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # таблица пользователей
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        registered_at TEXT,
        last_seen TEXT)""")
        # таблица сообщений пользователя
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        message_text TEXT
         timestamp TEXT)""")
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

# Функция для сохранения сообщения
def save_user_message(telegram_id: int, message_text: str):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO user_messages (telegram_id, message_text, timestamp)
        VALUES (?, ?, ?)""", (telegram_id, message_text, now))
        conn.commit()

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()

@router.message(Command("practice"))
@router.message(StateFilter(PracticeState.waiting_for_voice), F.voice | F.text)
async def practice_handler(message: Message, state: FSMContext, bot: Bot):

    current_state = await state.get_state()

    # 1) Старт практики (по /practice или если состояния нет)
    if current_state is None or (message.text and message.text.startswith("/practice")):
        # Сообщение о начале генерации
        await message.answer("Сейчас происходит генерация задания, пожалуйста, подождите...")

        # Генерируем задание
        exercise_text = await asyncio.to_thread(ai_service_exercise)
        await state.update_data(exercise_text=exercise_text)

        # Создаём TTS для задания
        tts_bytes = tts_gtts_mp3_bytes(exercise_text)
        tts_path = "tts.mp3"
        with open(tts_path, "wb") as f:
            f.write(tts_bytes)

        # Отправляем задание
        voice = FSInputFile(tts_path)
        await message.answer("Послушайте задание:")
        await message.answer_voice(voice)

        # Просим пользователя прислать голосовой ответ
        await message.answer(
            "Пожалуйста, запишите свой ответ голосом и нажмите кнопку ниже.",
        )

        # Ждём голос
        await state.set_state(PracticeState.waiting_for_voice)
        return

    # 2) Ожидание голосового сообщения
    if current_state == PracticeState.waiting_for_voice.state:
        # Если нет голосового — напомним
        if not message.voice:
            await message.answer("Пожалуйста, отправьте голосовое сообщение (нажмите удержание микрофона).")
            return

        # Сообщение о начале обработки
        processing_msg = await message.answer("Обработка вашего голосового сообщения... Пожалуйста, подождите.")

        # Скачиваем voice
        tg_file = await bot.get_file(message.voice.file_id)

        with tempfile.TemporaryDirectory() as td:
            ogg_path = os.path.join(td, "user_response.ogg")
            await bot.download_file(tg_file.file_path, destination=ogg_path)

            # Транскрибируем (пример с Whisper)
            user_text = transcribe_audio_file(
                ogg_path,
                model="whisper",
                language="en",
                ffmpeg_path=r"C:\\ffmpeg\\bin\\ffmpeg.exe"  # или "ffmpeg", если он в PATH
            )

        # Получаем обратную связь
        data = await state.get_data()
        exercise_text = data.get("exercise_text")
        feedback = ai_service(user_text, exercise_text)

        # Отправляем результат
        await message.answer(f"Ваш ответ: {user_text}")
        await message.answer(f"Обратная связь:\n{feedback}")

        # Завершаем сценарий
        await state.clear()
        try:
            await processing_msg.delete()
        except Exception:
            pass
        return


@router.message(Command('help'))
async def help(message: types.Message):
   faq_text = ("Ответы на частые вопросы:\nЧто нужно сделать, чтобы начать практиковать язык с ботом? "
                "\nПросто напишите команду /practice в диалоге с ботом. После этого бот предложит первые задания для практики. "
                "\nНа каких языках можно практиковаться с помощью бота?" 
                "\nВ настоящее время бот поддерживает английский язык. В будущем планируется расширение списка доступных языков. "
                "\nКак настроить сложность заданий под свой уровень?"
                "\nБот предлагает задания для уровня А1, А2, В1."
                "\nКак узнать, правильно ли я выполняю задания?"
                "\nБот автоматически проверяет ваши ответы и предоставляет обратную связь."
                "\nМогу ли я пользоваться ботом в любое время?"
                "\nДа, бот доступен 24/7 без ограничений по времени. "
                "Вы можете практиковать язык когда угодно и где угодно, главное — иметь доступ к интернету. Количество заданий и время использования не ограничены."
                )
   keyboard = create_help_keyboard()
   await message.answer(faq_text, reply_markup=keyboard)

@router.callback_query(F.data == 'ask_question')
async def process_ask_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer(
        "Пожалуйста, опишите ваш вопрос. Мы ответим вам в ближайшее время."
    )
    # Устанавливаем состояние ожидания вопроса
    await state.set_state(AskQuestion.waiting_for_question)
# === Обработчик ввода вопроса ===
@router.message(AskQuestion.waiting_for_question)
async def receive_question(message: types.Message, state: FSMContext):
    quest = message.text

    # Сохраняем сообщение пользователя в базу данных
    save_user_message(
        telegram_id=message.from_user.id,
        message_text=quest,
        timestamp=message.date.isoformat()
    )

    # Отправляем вопрос в функцию AI
    from ai_service import ai_service_faq
    answer = ai_service_faq(quest)

    # Проверяем результат
    if answer == "0":
        # Если функция не нашла ответ — пересылаем менеджеру
        await message.bot.send_message(
            MANAGER_CHAT_ID,
            f"❓ Новый вопрос от пользователя @{message.from_user.username or message.from_user.id}:\n\n{quest}"
        )
        await message.answer("Ваш вопрос передан менеджеру. Ожидайте ответа 🙏")
    else:
        # Если есть ответ — отправляем пользователю
        await message.answer(f"Ответ: {answer}")

    # Сбрасываем состояние
    await state.clear()

@router.message(Command(commands=["start"]))
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

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
