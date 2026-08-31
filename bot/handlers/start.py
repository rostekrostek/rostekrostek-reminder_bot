from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.main_menu import main_menu

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "йоу собаки, я нарута узумаки \nвыбери действие:",
        reply_markup=main_menu()
    )
