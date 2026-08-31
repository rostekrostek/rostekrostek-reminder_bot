# bot/scheduler/scheduler.py

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.async_session import SessionLocal
from db.models import Reminder, ReminderRecipient, User
from bot.data.users import USERS

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

scheduler = AsyncIOScheduler()


async def send_reminder(reminder_id: int, bot):
    async with SessionLocal() as session:

        # --- достаём напоминание ---
        result = await session.execute(
            select(Reminder)
            .options(
                joinedload(Reminder.recipients).joinedload(ReminderRecipient.user)
            )
            .where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()

        if not reminder:
            print(f"[scheduler] Напоминание {reminder_id} не найдено")
            return

        # --- достаём автора ---
        author_result = await session.execute(
            select(User).where(User.id == reminder.author_id)
        )
        author = author_result.scalar_one()
        author_name = author.name

        # === 🔥 УЧЁТ НАСТРОЕК АВТОРА ===
        if not author.notifications_enabled:
            print(f"[scheduler] Автор {author.telegram_id} отключил уведомления — пропускаем")
            return

        # --- формируем HTML‑список получателей ---
        rec_links = []
        for rec in reminder.recipients:
            uid = rec.user.telegram_id
            name = rec.user.name
            rec_links.append(f'<a href="tg://user?id={uid}">{name}</a>')
        rec_html = ", ".join(rec_links)

        # --- текст уведомления ---
        notify_text = (
            f"🔔 <b>Напоминание</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Текст:</b> {reminder.text}\n"
            f"📅 <b>Дата:</b> {reminder.target_datetime.strftime('%Y-%m-%d')}\n"
            f"⏰ <b>Время:</b> {reminder.target_datetime.strftime('%H:%M')}\n"
            f"👤 <b>Автор:</b> <a href=\"tg://user?id={author.telegram_id}\">{author_name}</a>\n"
            f"👥 <b>Получатели:</b> {rec_html}\n"
            f"⏳ <b>Предупредить за:</b> {reminder.notify_before_minutes} минут\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        # --- кнопка подтверждения ---
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✔️ Подтвердить", callback_data=f"confirm_reminder_{reminder.id}")]
        ])

        # --- отправляем уведомление каждому получателю ---
        for rec in reminder.recipients:

            # === 🔥 УЧЁТ НАСТРОЕК ПОЛУЧАТЕЛЯ ===
            if not rec.user.notifications_enabled:
                print(f"[scheduler] Получатель {rec.user.telegram_id} отключил уведомления — пропускаем")
                continue

            try:
                await bot.send_message(
                    rec.user.telegram_id,
                    notify_text,
                    reply_markup=kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"[scheduler] Ошибка отправки пользователю {rec.user.telegram_id}: {e}")


def schedule_reminder(reminder, bot):
    remind_at = reminder.target_datetime - timedelta(
        minutes=reminder.notify_before_minutes
    )

    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=remind_at,
        args=[reminder.id, bot]
    )


def start_scheduler():
    scheduler.start()
    print("[scheduler] APScheduler запущен")
