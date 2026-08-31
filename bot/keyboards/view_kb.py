from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def view_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📌 Мои созданные",
                callback_data="view_created"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Назначенные мне",
                callback_data="view_assigned"
            )
        ]
    ])


def reminders_list(reminders):
    kb = InlineKeyboardMarkup()

    for r in reminders:
        kb.add(
            InlineKeyboardButton(
                text=f"{r.text[:30]}...",
                callback_data=f"view_reminder_{r.id}"
            )
        )

    return kb


def back_to_view_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="view_back")]
    ])
