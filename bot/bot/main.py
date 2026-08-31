import asyncio
import sys

# Только для Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, YOUR_TELEGRAM_ID

# Routers
from bot.handlers.reminder_fsm import router as fsm_router
from bot.handlers.reminder_view import router as view_router
from bot.handlers.start import router as start_router
from bot.handlers.settings import router as settings_router



# Keyboards
from bot.keyboards.main_menu import main_menu

# Scheduler
from bot.scheduler.scheduler import start_scheduler


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры
    dp.include_router(fsm_router)
    dp.include_router(view_router)
    dp.include_router(start_router)
    dp.include_router(settings_router)

    # Запускаем APScheduler
    start_scheduler()

    # Отправляем стартовое меню (можно убрать)
    if YOUR_TELEGRAM_ID:
        try:
            await bot.send_message(
                chat_id=YOUR_TELEGRAM_ID,
                text="Бот запущен! 🚀",
                reply_markup=main_menu()
            )
        except Exception:
            pass

    # Старт long polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
