from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_keyboard(reminder_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✔ Подтвердить",
                callback_data=f"confirm_{reminder_id}"
            )
        ]
    ])
