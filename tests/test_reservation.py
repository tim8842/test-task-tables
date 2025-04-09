import pytest
from app.models import Table, Reservation, ReservationWithValidation
import pytest_asyncio
from datetime import datetime, timedelta
from conftest import clear_db

API_VERSION = "/api/v1"
TEST_ROUTE_RESERVATION = "/reservations"


@pytest_asyncio.fixture(scope="function")
async def add_test_data_reservation(clear_db, db_session):
    test_table_1 = Table(name="Test Table 1", seats=3, location="window")
    db_session.add(test_table_1)
    reservation = Reservation(
        customer_name="valentin",
        table_id=1,
        reservation_time=datetime.now(),
        duration_minutes=30,
    )
    db_session.add(reservation)
    await db_session.commit()
    return [reservation]


# тест получения всех броней
@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_reservations(add_test_data_reservation, session):
    response = await session.get(API_VERSION + TEST_ROUTE_RESERVATION)
    assert response.status_code == 200
    assert "reservations" in response.json()
    reservations = response.json()["reservations"]
    assert isinstance(reservations, list)
    assert len(reservations) == len(add_test_data_reservation)
    assert add_test_data_reservation[0].customer_name in [
        reservation["customer_name"] for reservation in reservations
    ]


# тест на вставку и пересечение
@pytest.mark.asyncio(loop_scope="session")
async def test_insert_table(db_session, session):
    response = await session.post(
        API_VERSION + TEST_ROUTE_RESERVATION,
        json={
            "customer_name": "vadim",
            "table_id": 1,
            "reservation_time": datetime.now().isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 400
    response = await session.post(
        API_VERSION + TEST_ROUTE_RESERVATION,
        json={
            "customer_name": "vadim",
            "table_id": 1,
            "reservation_time": datetime.now().isoformat(),
            "duration_minutes": 0,
        },
    )
    assert response.status_code == 422
    response = await session.post(
        API_VERSION + TEST_ROUTE_RESERVATION,
        json={
            "customer_name": "oksana",
            "table_id": 1,
            "reservation_time": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 400
    response = await session.post(
        API_VERSION + TEST_ROUTE_RESERVATION,
        json={
            "customer_name": "olya",
            "table_id": 1,
            "reservation_time": (datetime.now() + timedelta(minutes=35)).isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 200
    assert "reservation" in response.json()
    reservation = response.json()["reservation"]
    assert reservation["customer_name"] == "olya"
    assert (
        await Reservation.getById(db_session, reservation["id"])
    ).customer_name == reservation["customer_name"]


# Тест на удаление
@pytest.mark.asyncio(
    loop_scope="session",
)
async def test_delete_table(session):
    response = await session.delete(API_VERSION + TEST_ROUTE_RESERVATION + "/99")
    assert response.status_code == 400
    response = await session.delete(API_VERSION + TEST_ROUTE_RESERVATION + "/1")
    assert "reservation" in response.json()
    reservation = response.json()["reservation"]
    assert reservation["customer_name"] == "valentin"
