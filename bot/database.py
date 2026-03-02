import json
from functools import partial
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool, "echo": False}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {"echo": True}

# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# psycopg2 - sync engine

engine = create_async_engine(DATABASE_URL, json_serializer=partial(json.dumps, ensure_ascii=False),
                             **DATABASE_PARAMS)

# async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    _test_data = list()

    @classmethod
    def get_test_data(cls):
        return cls._test_data

    @classmethod
    def set_test_data(cls, value: list[dict]):
        cls._test_data = value
