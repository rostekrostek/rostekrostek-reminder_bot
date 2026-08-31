from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def date_picker():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="date_today")],
        [InlineKeyboardButton(text="Завтра", callback_data="date_tomorrow")],
        [InlineKeyboardButton(text="Выбрать вручную", callback_data="date_manual")]
    ])

def time_picker():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="09:00", callback_data="time_09_00")],
        [InlineKeyboardButton(text="12:00", callback_data="time_12_00")],
        [InlineKeyboardButton(text="18:00", callback_data="time_18_00")],
        [InlineKeyboardButton(text="Выбрать вручную", callback_data="time_manual")]
    ])

def notify_before_picker():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="10 минут", callback_data="nb_10")],
        [InlineKeyboardButton(text="30 минут", callback_data="nb_30")],
        [InlineKeyboardButton(text="1 час", callback_data="nb_60")],
        [InlineKeyboardButton(text="2 часа", callback_data="nb_120")],
    ])
