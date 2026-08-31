@router.callback_query(ReminderStates.recipients)
async def step_recipients_choice(call: CallbackQuery, state: FSMContext):
    data = call.data

    if data == "recipients_done":
        await state.set_state(ReminderStates.notify_before)
        await call.message.edit_text("За сколько предупредить?", reply_markup=notify_before_picker())
        return

    user_id = int(data.split("_")[1])
    st = await state.get_data()
    recipients = st.get("recipients", [])

    if user_id not in recipients:
        recipients.append(user_id)

    await state.update_data(recipients=recipients)
    await call.answer("Добавлено!")


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
