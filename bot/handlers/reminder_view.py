from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from db.async_session import SessionLocal

from db.services.reminder_service import ReminderService

from bot.keyboards.view_kb import view_menu, reminders_list, back_to_view_menu

router = Router()


# ---------------------------------------------------------
# /my — старт просмотра
# ---------------------------------------------------------
@router.message(F.text == "/my")
async def my_reminders(msg: Message):
    await msg.answer(
        "Выбери, что показать:",
        reply_markup=view_menu()
    )


# ---------------------------------------------------------
# Мои созданные
# ---------------------------------------------------------
@router.callback_query(F.data == "view_created")
async def view_created(call: CallbackQuery):
    async with SessionLocal() as session:
        service = ReminderService(session)

        user = await service.get_or_create_user(
            telegram_id=call.from_user.id,
            name=call.from_user.full_name
        )

        reminders = await service.get_user_reminders(user.id)

        # фильтруем: только созданные
        created = [r for r in reminders if r.author_id == user.id]

    if not created:
        await call.message.edit_text(
            "У тебя нет созданных напоминаний.",
            reply_markup=back_to_view_menu()
        )
        return

    await call.message.edit_text(
        "📌 Твои созданные напоминания:",
        reply_markup=reminders_list(created)
    )


# ---------------------------------------------------------
# Назначенные мне
# ---------------------------------------------------------
@router.callback_query(F.data == "view_assigned")
async def view_assigned(call: CallbackQuery):
    async with SessionLocal() as session:
        service = ReminderService(session)

        user = await service.get_or_create_user(
            telegram_id=call.from_user.id,
            name=call.from_user.full_name
        )

        reminders = await service.get_user_reminders(user.id)

        # фильтруем: только назначенные
        assigned = [
            r for r in reminders
            if any(rec.user_id == user.id for rec in r.recipients)
        ]

    if not assigned:
        await call.message.edit_text(
            "Тебе ничего не назначено.",
            reply_markup=back_to_view_menu()
        )
        return

    await call.message.edit_text(
        "🎯 Напоминания, назначенные тебе:",
        reply_markup=reminders_list(assigned)
    )


# ---------------------------------------------------------
# Просмотр конкретного напоминания
# ---------------------------------------------------------
@router.callback_query(F.data.startswith("view_reminder_"))
async def view_reminder(call: CallbackQuery):
    reminder_id = int(call.data.split("_")[2])

    async with SessionLocal() as session:
        service = ReminderService(session)
        reminder = await session.get(type(service).__dict__["create_reminder"].__annotations__["return"], reminder_id)

    if not reminder:
        await call.message.edit_text(
            "Напоминание не найдено.",
            reply_markup=back_to_view_menu()
        )
        return

    recipients = ", ".join([rec.user.name for rec in reminder.recipients])

    text = (
        f"📝 <b>{reminder.text}</b>\n\n"
        f"📅 Дата: {reminder.target_datetime.date()}\n"
        f"⏰ Время: {reminder.target_datetime.time()}\n"
        f"👤 Автор: {reminder.author.name}\n"
        f"👥 Получатели: {recipients}\n"
        f"⏳ Предупредить за: {reminder.notify_before_minutes} мин\n"
    )

    await call.message.edit_text(
        text,
        reply_markup=back_to_view_menu(),
        parse_mode="HTML"
    )


# ---------------------------------------------------------
# Назад
# ---------------------------------------------------------
@router.callback_query(F.data == "view_back")
async def view_back(call: CallbackQuery):
    await call.message.edit_text(
        "Выбери, что показать:",
        reply_markup=view_menu()
    )
