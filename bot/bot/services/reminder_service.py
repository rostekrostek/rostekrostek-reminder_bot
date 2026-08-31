from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from db.async_session import SessionLocal
from db.models import User, Reminder, ReminderRecipient, ReminderLog


class ReminderService:

    # -----------------------------
    # USERS
    # -----------------------------
    async def _get_or_create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        name: str = None,
        default_timezone: str = "UTC",
    ) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                name=name or str(telegram_id),
                timezone=default_timezone,
            )
            session.add(user)
            await session.flush()

        return user

    async def get_or_create_user(self, telegram_id: int, name: str = None) -> User:
        async with SessionLocal() as session:
            user = await self._get_or_create_user(session, telegram_id, name=name)
            await session.commit()
            await session.refresh(user)
            return user

    async def update_timezone(self, telegram_id: int, timezone: str) -> None:
        async with SessionLocal() as session:
            user = await self._get_or_create_user(session, telegram_id)
            user.timezone = timezone
            await session.commit()

    async def update_notifications(self, telegram_id: int, enabled: bool) -> None:
        async with SessionLocal() as session:
            user = await self._get_or_create_user(session, telegram_id)
            user.notifications_enabled = enabled
            await session.commit()

    # -----------------------------
    # REMINDER CREATION
    # -----------------------------
    async def create_reminder(
        self,
        telegram_id: int,
        text: str,
        date_str: str,
        time_str: str,
        notify_before: int,
        recipients: List[int],
    ) -> Reminder:

        async with SessionLocal() as session:
            author = await self._get_or_create_user(session, telegram_id)
            user_tz = author.timezone or "UTC"

            target_dt = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )

            reminder = Reminder(
                author_id=author.id,
                text=text,
                target_datetime=target_dt,
                notify_before_minutes=notify_before,
            )
            session.add(reminder)
            await session.flush()

            for uid in recipients:
                user = await self._get_or_create_user(session, uid, default_timezone=user_tz)

                rr = ReminderRecipient(
                    reminder_id=reminder.id,
                    user_id=user.id,
                )
                session.add(rr)

            await session.commit()

            # перечитываем со всеми связями, чтобы объект был пригоден
            # для использования после закрытия сессии (schedule_reminder и т.п.)
            result = await session.execute(
                select(Reminder)
                .options(
                    joinedload(Reminder.recipients).joinedload(ReminderRecipient.user),
                    joinedload(Reminder.author),
                )
                .where(Reminder.id == reminder.id)
            )
            return result.unique().scalar_one()

    # -----------------------------
    # READ
    # -----------------------------
    async def get_user_reminders(self, telegram_id: int):
        """Возвращает напоминания, где пользователь — автор или получатель."""
        async with SessionLocal() as session:
            user = await self._get_or_create_user(session, telegram_id)
            await session.commit()

            stmt = (
                select(Reminder)
                .outerjoin(ReminderRecipient, Reminder.id == ReminderRecipient.reminder_id)
                .options(
                    joinedload(Reminder.recipients).joinedload(ReminderRecipient.user),
                    joinedload(Reminder.author),
                )
                .where(
                    (Reminder.author_id == user.id)
                    | (ReminderRecipient.user_id == user.id)
                )
                .order_by(Reminder.target_datetime.asc())
            )
            result = await session.execute(stmt)
            return result.unique().scalars().all()

    async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        async with SessionLocal() as session:
            stmt = (
                select(Reminder)
                .options(
                    joinedload(Reminder.recipients).joinedload(ReminderRecipient.user),
                    joinedload(Reminder.author),
                )
                .where(Reminder.id == reminder_id)
            )
            result = await session.execute(stmt)
            return result.unique().scalar_one_or_none()

    # -----------------------------
    # DELETE
    # -----------------------------
    async def delete_reminder(self, reminder_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                delete(ReminderRecipient).where(ReminderRecipient.reminder_id == reminder_id)
            )
            await session.execute(
                delete(ReminderLog).where(ReminderLog.reminder_id == reminder_id)
            )
            await session.execute(
                delete(Reminder).where(Reminder.id == reminder_id)
            )
            await session.commit()

    # -----------------------------
    # CONFIRMATION
    # -----------------------------
    async def confirm_reminder(self, reminder_id: int, telegram_id: int) -> Optional[ReminderRecipient]:
        """Подтверждение напоминания получателем (по его telegram_id)."""
        async with SessionLocal() as session:
            user = await self._get_or_create_user(session, telegram_id)

            result = await session.execute(
                select(ReminderRecipient).where(
                    ReminderRecipient.reminder_id == reminder_id,
                    ReminderRecipient.user_id == user.id,
                )
            )
            rec = result.scalar_one_or_none()

            if not rec:
                await session.commit()
                return None

            rec.is_confirmed = True
            rec.confirmed_at = datetime.utcnow()

            session.add(ReminderLog(
                reminder_id=reminder_id,
                user_id=user.id,
                event_type="confirmed",
                timestamp=datetime.utcnow(),
            ))

            await session.commit()
            return rec

    async def add_log(self, reminder_id: int, user_id: Optional[int], event_type: str) -> None:
        async with SessionLocal() as session:
            session.add(ReminderLog(
                reminder_id=reminder_id,
                user_id=user_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
            ))
            await session.commit()


service = ReminderService()
