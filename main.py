import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN, API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('help'))
async def help(message: Message):
   await message.answer("Этот бот умеет выполнять команды:\n/start \n/help \n/practice \n/support")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, этот бот для практики иностранного языка!")



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())