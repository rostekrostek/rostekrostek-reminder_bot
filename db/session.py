import os

DB_URL = os.getenv("DATABASE_URL").replace("asyncpg", "psycopg2")
