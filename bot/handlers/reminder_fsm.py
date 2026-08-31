from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from bot.states.reminder_states import ReminderStates
from bot.keyboards.reminder_kb import date_picker, time_picker, notify_before_picker
from bot.keyboards.main_menu import main_menu
from bot.scheduler.scheduler import schedule_reminder
from bot.services.reminder_service import service
from bot.data.users import USERS

router = Router()


# ============================
# ШАГ 1 — старт создания
# ============================
@router.callback_query(F.data == "create_reminder")
async def step_date(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.date)
    await call.message.edit_text("Выбери дату:", reply_markup=date_picker())


# ============================
# ШАГ 2 — выбор даты
# ============================
@router.callback_query(ReminderStates.date, F.data.startswith("date_"))
async def step_time(call: CallbackQuery, state: FSMContext):
    data = call.data

    if data == "date_today":
        chosen_date = datetime.now().date()
    elif data == "date_tomorrow":
        chosen_date = datetime.now().date() + timedelta(days=1)
    else:
        await call.message.edit_text("Введи дату вручную (YYYY-MM-DD):")
        return

    await state.update_data(date=str(chosen_date))
    await state.set_state(ReminderStates.time)

    await call.message.edit_text("Выбери время:", reply_markup=time_picker())


# --- ручной ввод даты ---
@router.message(ReminderStates.date)
async def manual_date(msg: Message, state: FSMContext):
    try:
        chosen_date = datetime.strptime(msg.text, "%Y-%m-%d").date()
    except:
        await msg.answer("Неверный формат. Пример: 2026-08-29")
        return

    await state.update_data(date=str(chosen_date))
    await state.set_state(ReminderStates.time)

    await msg.answer("Выбери время:", reply_markup=time_picker())


# ============================
# ШАГ 3 — выбор времени
# ============================
@router.callback_query(ReminderStates.time, F.data.startswith("time_"))
async def step_text(call: CallbackQuery, state: FSMContext):
    data = call.data

    if data == "time_manual":
        await call.message.edit_text("Введи время вручную (HH:MM):")
        return

    _, hh, mm = data.split("_")
    chosen_time = f"{hh}:{mm}"

    await state.update_data(time=chosen_time)
    await state.set_state(ReminderStates.text)

    await call.message.edit_text("Введи текст напоминания:")


# --- ручной ввод времени ---
@router.message(ReminderStates.time)
async def manual_time(msg: Message, state: FSMContext):
    try:
        datetime.strptime(msg.text, "%H:%M")
    except:
        await msg.answer("Неверный формат. Пример: 09:30")
        return

    await state.update_data(time=msg.text)
    await state.set_state(ReminderStates.text)

    await msg.answer("Введи текст напоминания:")


# ============================
# ШАГ 4 — ввод текста
# ============================
@router.message(ReminderStates.text)
async def step_recipients(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await state.set_state(ReminderStates.recipients)

    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"rec_{uid}")]
        for uid, name in USERS.items()
    ]
    buttons.append([InlineKeyboardButton(text="Готово", callback_data="recipients_done")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await msg.answer("Выбери получателей:", reply_markup=kb)


# ============================
# ШАГ 4.1 — выбор получателей
# ============================
@router.callback_query(ReminderStates.recipients)
async def step_recipients_choice(call: CallbackQuery, state: FSMContext):
    data = call.data

    # кнопка "Готово"
    if data == "recipients_done":
        await state.set_state(ReminderStates.notify_before)
        await call.message.edit_text("За сколько предупредить?", reply_markup=notify_before_picker())
        return

    # выбор пользователя
    if data.startswith("rec_"):
        user_id = int(data.split("_")[1])

        st = await state.get_data()
        recipients = st.get("recipients", [])

        if user_id not in recipients:
            recipients.append(user_id)

        await state.update_data(recipients=recipients)
        await call.answer("Добавлено!")
        return

    # fallback
    await call.answer("Неизвестная команда")


# ============================
# ШАГ 5 — выбор notify_before
# ============================
@router.callback_query(ReminderStates.notify_before, F.data.startswith("nb_"))
async def step_confirm(call: CallbackQuery, state: FSMContext):
    minutes = int(call.data.split("_")[1])
    await state.update_data(notify_before=minutes)
    await state.set_state(ReminderStates.confirm)

    data = await state.get_data()

    recipients = data.get("recipients", [])
    rec_html = ", ".join([USERS.get(r, "Пользователь") for r in recipients]) if recipients else "нет"

    text = (
        f"🔔 <b>Подтверждение создания</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Текст:</b> {data['text']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"⏰ <b>Время:</b> {data['time']}\n"
        f"👥 <b>Получатели:</b> {rec_html}\n"
        f"⏳ <b>За:</b> {minutes} минут\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Создать напоминание?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать", callback_data="confirm_create")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_create")],
    ])

    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ============================
# ШАГ 6 — подтверждение и создание
# ============================
@router.callback_query(ReminderStates.confirm, F.data == "confirm_create")
async def finish(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    recipients = data.get("recipients", [])
    author_id = call.from_user.id
    author_name = USERS.get(author_id, "Автор")

    rec_links = []
    for uid in recipients:
        name = USERS.get(uid, "Пользователь")
        rec_links.append(f'<a href="tg://user?id={uid}">{name}</a>')
    rec_html = ", ".join(rec_links)

    reminder = await service.create_reminder(
        telegram_id=author_id,
        text=data["text"],
        date_str=data["date"],
        time_str=data["time"],
        notify_before=data["notify_before"],
        recipients=recipients,
    )

    schedule_reminder(reminder, call.bot)

    notify_text = (
        f"🔔 <b>Тебе назначили напоминание!</b>\n\n"
        f"👤 Автор: <a href=\"tg://user?id={author_id}\">{author_name}</a>\n"
        f"📝 Текст: {data['text']}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"👥 Получатели: {rec_html}\n"
        f"⏳ Предупредить за: {data['notify_before']} минут\n"
    )

    for uid in recipients:
        try:
            await call.bot.send_message(uid, notify_text, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка отправки уведомления пользователю {uid}: {e}")

    await call.message.edit_text(
        "Напоминание создано! 🎉",
        reply_markup=main_menu()
    )

    await state.clear()


@router.callback_query(ReminderStates.confirm, F.data == "cancel_create")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Создание отменено.", reply_markup=main_menu())
    await state.clear()
