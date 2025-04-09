import pytest
import psycopg2
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import Table, Reservation
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

DATABASE_URL = f"postgresql+asyncpg://{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOST")}/{config("TEST_DB_NAME")}"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    create_test_db()
    await create_tables()
    yield
    await drop_tables()
    drop_test_db()


def create_test_db():
    host = config("POSTGRES_HOST")
    port = host.split(":")[-1]
    host = host.split(":")[0]
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=config("POSTGRES_USER"),
        password=config("POSTGRES_PASSWORD"),
        dbname=config("POSTGRES_DB"),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE {config('TEST_DB_NAME')}")
    cursor.close()
    connection.close()


def drop_test_db():
    host = config("POSTGRES_HOST")
    port = host.split(":")[-1]
    host = host.split(":")[0]
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=config("POSTGRES_USER"),
        password=config("POSTGRES_PASSWORD"),
        dbname=config("POSTGRES_DB"),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(
        f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{config('TEST_DB_NAME')}'
        AND pid <> pg_backend_pid();
    """
    )
    cursor.execute(f"DROP DATABASE IF EXISTS {config('TEST_DB_NAME')}")
    cursor.close()
    connection.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def db_session():

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def clear_db(db_session):
    await db_session.execute(Reservation.__table__.delete())
    await db_session.execute(Table.__table__.delete())
    await db_session.commit()


@pytest_asyncio.fixture(autouse=True)
async def override_dependency(db_session):
    app.dependency_overrides[get_db] = lambda: db_session


@pytest_asyncio.fixture(scope="session")
async def session():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8005"
    ) as ac:
        yield ac
