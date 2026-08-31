# bot/handlers/reminder_confirm.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states.reminder_states import ReminderStates
from bot.scheduler.scheduler import schedule_reminder
from bot.services.reminder_service import service

router = Router()


@router.callback_query(ReminderStates.confirm, F.data == "  confirm_create")
async def finish(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    recipients = data.get("recipients", [])

    reminder = await service.create_reminder(
        telegram_id=call.from_user.id,
        text=data["text"],
        date_str=data["date"],
        time_str=data["time"],
        notify_before=data["notify_before"],
        recipients=recipients,
    )
    # планируем задачу
    schedule_reminder(reminder, call.bot)

    await call.message.edit_text("Напоминание создано! 🎉")
    await state.clear()


@router.callback_query(ReminderStates.confirm, F.data == "cancel_create")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Создание отменено.")
    await state.clear()
