from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Reminder, ReminderRecipient, ReminderLog


class ReminderService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # USERS
    # -----------------------------
    async def get_or_create_user(self, telegram_id: int, name: str = None):
        """Возвращает пользователя или создаёт нового."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            name=name or f"User {telegram_id}",
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # -----------------------------
    # REMINDER CREATION
    # -----------------------------
    async def create_reminder(
        self,
        author_id: int,
        text: str,
        date_str: str,
        time_str: str,
        notify_before: int,
        recipients: list[int],
    ):
        """Создаёт напоминание + получателей."""

        # 1. Собираем datetime
        target_datetime = datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )

        # 2. Создаём напоминание
        reminder = Reminder(
            author_id=author_id,
            text=text,
            target_datetime=target_datetime,
            notify_before_minutes=notify_before,
            created_at=datetime.utcnow(),
        )

        self.session.add(reminder)
        await self.session.flush()  # reminder.id появляется здесь

        # 3. Добавляем получателей
        for user_id in recipients:
            recipient = ReminderRecipient(
                reminder_id=reminder.id,
                user_id=user_id,
                is_confirmed=False,
                confirmed_at=None,
            )
            self.session.add(recipient)

        await self.session.commit()
        await self.session.refresh(reminder)

        return reminder

    # -----------------------------
    # LOGS
    # -----------------------------
    async def add_log(self, reminder_id: int, user_id: int | None, event_type: str):
        """Добавляет запись в лог."""
        log = ReminderLog(
            reminder_id=reminder_id,
            user_id=user_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
        )
        self.session.add(log)
        await self.session.commit()
        return log

    # -----------------------------
    # CONFIRMATION
    # -----------------------------
    async def confirm_reminder(self, reminder_id: int, user_id: int):
        """Подтверждение напоминания получателем."""
        result = await self.session.execute(
            select(ReminderRecipient).where(
                ReminderRecipient.reminder_id == reminder_id,
                ReminderRecipient.user_id == user_id,
            )
        )
        rec = result.scalar_one_or_none()

        if not rec:
            return None

        rec.is_confirmed = True
        rec.confirmed_at = datetime.utcnow()

        await self.session.commit()
        await self.add_log(reminder_id, user_id, "confirmed")

        return rec

    # -----------------------------
    # GET REMINDERS FOR USER
    # -----------------------------
    async def get_user_reminders(self, user_id: int):
        """Возвращает напоминания, где пользователь — автор или получатель."""
        result = await self.session.execute(
            select(Reminder)
            .join(ReminderRecipient, Reminder.id == ReminderRecipient.reminder_id)
            .where(
                (Reminder.author_id == user_id)
                | (ReminderRecipient.user_id == user_id)
            )
        )
        return result.scalars().all()
