import os

_raw_url = os.getenv("DATABASE_URL")
if not _raw_url:
    raise RuntimeError("DATABASE_URL не задан — проверь .env / переменные окружения")

DB_URL = _raw_url.replace("asyncpg", "psycopg2")
