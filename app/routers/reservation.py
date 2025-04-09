from fastapi import APIRouter, Depends, Path
from ..models import Reservation, ReservationWithValidation
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.reservation import RequestCreateReservation

router = APIRouter()


@router.get("")
async def get_all_reservations(db: AsyncSession = Depends(get_db)):
    reservations = await Reservation.getAll(db)
    return {"reservations": reservations}


@router.post("")
async def create_reservation(
    reservation: RequestCreateReservation, db: AsyncSession = Depends(get_db)
):
    reservation = reservation.model_dump()
    reservation = await ReservationWithValidation.create(db, **reservation)
    return {"reservation": reservation}


@router.delete("/{id}")
async def delete_reservation(id: int = Path(...), db: AsyncSession = Depends(get_db)):
    reservation = await Reservation.deleteById(db, id)
    return {"reservation": reservation}
