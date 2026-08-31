from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.keyboards.main_menu import main_menu

router = Router()

# Главное меню настроек
def settings_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕒 Часовой пояс", callback_data="settings_timezone")],
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")],
    ])
    return kb


@router.callback_query(F.data == "settings")
async def open_settings(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ <b>Настройки</b>\nВыбери категорию:",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )


# ===== Часовой пояс =====

@router.callback_query(F.data == "settings_timezone")
async def settings_timezone(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="UTC", callback_data="tz_UTC")],
        [InlineKeyboardButton(text="Europe/Moscow", callback_data="tz_Moscow")],
        [InlineKeyboardButton(text="Europe/Paris", callback_data="tz_Paris")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")],
    ])

    await call.message.edit_text(
        "🕒 <b>Выбери часовой пояс:</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tz_"))
async def timezone_selected(call: CallbackQuery):
    tz = call.data.split("_")[1]

    from bot.services.reminder_service import service
    await service.update_timezone(call.from_user.id, tz)

    await call.message.edit_text(
        f"🕒 Часовой пояс установлен: <b>{tz}</b>",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )


# ===== Уведомления =====

@router.callback_query(F.data == "settings_notifications")
async def settings_notifications(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Включить", callback_data="notif_on")],
        [InlineKeyboardButton(text="Выключить", callback_data="notif_off")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")],
    ])

    await call.message.edit_text(
        "🔔 <b>Уведомления</b>\nВыбери действие:",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "notif_on")
async def notif_on(call: CallbackQuery):
    from bot.services.reminder_service import service
    await service.update_notifications(call.from_user.id, True)

    await call.message.edit_text(
        "🔔 Уведомления включены!",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "notif_off")
async def notif_off(call: CallbackQuery):
    from bot.services.reminder_service import service
    await service.update_notifications(call.from_user.id, False)

    await call.message.edit_text(
        "🔕 Уведомления выключены!",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )


# ===== Назад в главное меню =====

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text(
        "Выбери действие:",
        reply_markup=main_menu()
    )
