# bot/states/reminder_states.py

from aiogram.fsm.state import StatesGroup, State

class ReminderStates(StatesGroup):
    date = State()
    time = State()
    text = State()
    recipients = State()
    notify_before = State()
    confirm = State()
