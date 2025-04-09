from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, DeclarativeBase
from decouple import config
from abc import ABCMeta

DATABASE_URL = f"postgresql+asyncpg://{config('POSTGRES_USER')}:{config('POSTGRES_PASSWORD')}@{config('POSTGRES_HOST')}/{config('POSTGRES_DB')}"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


# класс который позволяет объединить 2 метакласса
class BaseMeta(ABCMeta, type(declarative_base())):
    pass


Base: DeclarativeBase = declarative_base(metaclass=BaseMeta)


async def get_db():
    async with async_session() as session:
        yield session
        await session.close()
