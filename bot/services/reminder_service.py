from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.async_session import SessionLocal
from db.models import User, Reminder, ReminderRecipient


class ReminderService:

    async def _get_or_create_user(
        self,
        session: AsyncSession,
        telegram_id: int,
        default_timezone: str = "UTC",
    ) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                name=str(telegram_id),
                timezone=default_timezone,
            )
            session.add(user)
            await session.flush()

        return user

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
            # автор
            author = await self._get_or_create_user(session, telegram_id)
            user_tz = author.timezone or "UTC"

            # дата-время
            target_dt = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )

            # создаём напоминание
            reminder = Reminder(
                author_id=author.id,
                text=text,
                target_datetime=target_dt,
                notify_before_minutes=notify_before,
            )
            session.add(reminder)
            await session.flush()

            # создаём получателей
            for uid in recipients:
                user = await self._get_or_create_user(session, uid, user_tz)

                rr = ReminderRecipient(
                    reminder_id=reminder.id,
                    user_id=user.id,
                )
                session.add(rr)

            await session.commit()
            await session.refresh(reminder)

            return reminder

    async def get_user_reminders(self, telegram_id: int):
        async with SessionLocal() as session:
            stmt = (
                select(Reminder)
                .join(User, Reminder.author_id == User.id)
                .where(User.telegram_id == telegram_id)
                .order_by(Reminder.target_datetime.asc())
            )
            result = await session.execute(stmt)
            return result.scalars().unique().all()

    async def delete_reminder(self, reminder_id: int) -> None:
        async with SessionLocal() as session:
            stmt = delete(Reminder).where(Reminder.id == reminder_id)
            await session.execute(stmt)
            await session.commit()

    async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        async with SessionLocal() as session:
            stmt = select(Reminder).where(Reminder.id == reminder_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()


service = ReminderService()
