@router.callback_query(ReminderStates.recipients, F.data.startswith("rec_"))
async def step_recipients_choice(call: CallbackQuery, state: FSMContext):
    data = call.data
    user_id = int(data.split("_")[1])

    st = await state.get_data()
    recipients = st.get("recipients", [])

    if user_id not in recipients:
        recipients.append(user_id)

    await state.update_data(recipients=recipients)
    await call.answer("Добавлено!")
