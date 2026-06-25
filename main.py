import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Получаем токен бота из переменных окружения Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для создания приветственной клавиатуры (если нужны просто кнопки-ссылки)
def get_welcome_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🌐 Открыть сервис / Open Service", 
        url="https://your-website-or-app.com"  # Укажите вашу ссылку, если она нужна
    ))
    return builder.as_markup()

# Обработка команды /start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    text = (
        "👋 **Добро пожаловать!**\n\n"
        "Все функции сервиса успешно активированы и доступны для вас.\n\n"
        "👋 **Welcome!**\n\n"
        "All features of the service are successfully activated and available for you."
    )
    # Если кнопка-ссылка не нужна, можно убрать reply_markup=get_welcome_keyboard()
    await message.answer(text, parse_mode="Markdown", reply_markup=get_welcome_keyboard())

# Главная функция запуска бота
async def main():
    print("Бот успешно запущен в штатном режиме...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())