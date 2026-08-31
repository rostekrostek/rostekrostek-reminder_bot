import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

ASYNC_DB_URL = os.getenv("DATABASE_URL")  # ← ВАЖНО

engine = create_async_engine(ASYNC_DB_URL, echo=False)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)
