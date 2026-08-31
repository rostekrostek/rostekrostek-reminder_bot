from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
        [InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    ])
    return kb
