import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message

from embedding import generate_data_for_final_response

# Установите уровень логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
TOKEN = '7901231896:AAG9eimhNHdee-Eg8lxde2yYjm2NdDb1GZA'

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Задайте свой вопрос о MetaMask.")

@dp.message()
async def handle_message(message: types.Message):
    user_question = message.text
    response = generate_data_for_final_response(user_question)
    await message.reply(response)


async def main() -> None:
    # Запуск обработки обновлений
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())







