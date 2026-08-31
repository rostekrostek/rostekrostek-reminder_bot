from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# -----------------------------
# USERS
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    notifications_enabled = Column(Boolean, default=True)

    reminders_created = relationship("Reminder", back_populates="author")
    reminder_targets = relationship("ReminderRecipient", back_populates="user")


# -----------------------------
# REMINDERS
# -----------------------------
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    text = Column(String, nullable=False)
    target_datetime = Column(DateTime, nullable=False)
    notify_before_minutes = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="reminders_created")
    recipients = relationship("ReminderRecipient", back_populates="reminder")
    logs = relationship("ReminderLog", back_populates="reminder")


# -----------------------------
# RECIPIENTS
# -----------------------------
class ReminderRecipient(Base):
    __tablename__ = "reminder_recipients"

    id = Column(Integer, primary_key=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)

    reminder = relationship("Reminder", back_populates="recipients")
    user = relationship("User", back_populates="reminder_targets")


# -----------------------------
# LOGS
# -----------------------------
class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    event_type = Column(String, nullable=False)  # sent_early / sent_target / repeat / confirmed
    timestamp = Column(DateTime, default=datetime.utcnow)

    reminder = relationship("Reminder", back_populates="logs")
