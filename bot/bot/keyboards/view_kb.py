from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
    builder = InlineKeyboardBuilder()

    for r in reminders:
        label = r.text if len(r.text) <= 30 else f"{r.text[:30]}..."
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"view_reminder_{r.id}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅ Назад", callback_data="view_back")
    )

    return builder.as_markup()


def back_to_view_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="view_back")]
    ])
