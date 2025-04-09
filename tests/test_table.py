import pytest
from app.models import Table
import pytest_asyncio
from conftest import clear_db

API_VERSION = "/api/v1"
TEST_ROUTE_TABLES = "/tables"


@pytest_asyncio.fixture(scope="function")
async def add_test_data(clear_db, db_session):
    test_table_1 = Table(name="Test Table 1", seats=3, location="window")
    test_table_2 = Table(name="Test Table 2", seats=4, location="window")
    db_session.add(test_table_1)
    db_session.add(test_table_2)
    await db_session.commit()
    return [test_table_1, test_table_2]


# тест получения всех столов
@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_tables(add_test_data, session):
    response = await session.get(API_VERSION + TEST_ROUTE_TABLES)
    assert response.status_code == 200
    assert "tables" in response.json()
    tables = response.json()["tables"]
    assert isinstance(tables, list)
    assert len(tables) == len(add_test_data)
    assert add_test_data[0].name in [table["name"] for table in tables]
    assert add_test_data[1].name in [table["name"] for table in tables]


# тест на вставку стола
@pytest.mark.asyncio(loop_scope="session")
async def test_insert_table(db_session, session):
    response = await session.post(
        API_VERSION + TEST_ROUTE_TABLES,
        json={"name": "table 1", "seats": 5, "location": "window"},
    )
    assert response.status_code == 200
    assert "table" in response.json()
    table = response.json()["table"]
    assert table["name"] == "table 1"
    assert (await Table.getById(db_session, table["id"])).name == table["name"]
    response = await session.post(
        API_VERSION + TEST_ROUTE_TABLES,
        json={"name": "table 1", "seats": -1, "location": "window"},
    )
    assert response.status_code == 422


# Тест на удаление
@pytest.mark.asyncio(loop_scope="session")
async def test_delete_table(add_test_data, session):

    response = await session.delete(
        API_VERSION + TEST_ROUTE_TABLES + f"/{add_test_data[0].id}"
    )
    assert "table" in response.json()
    table = response.json()["table"]
    assert table["name"] == "Test Table 1"
    response = await session.delete(API_VERSION + TEST_ROUTE_TABLES + "/99")
    assert response.status_code == 400
