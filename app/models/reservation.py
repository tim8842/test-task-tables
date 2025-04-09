from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, CheckConstraint, ForeignKey, DateTime
from ..database import Base
from datetime import datetime
from .base import BaseDao
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.sql import exists, func
from datetime import timedelta
from sqlalchemy.dialects.postgresql import INTERVAL


class Reservation(Base, BaseDao):
    __table_args__ = (
        # CheckConstraint('reservation_time > CURRENT_TIMESTAMP', name='check_reservation_time_future'),
        # если нужно чтобы нельзя было на прошлое забронировать
        CheckConstraint("duration_minutes > 0", name="check_duration_minutes_positive"),
    )
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String)
    table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    reservation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    table = relationship("Table", back_populates="reservations")


class ReservationWithValidation(Reservation):
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        reservation_time = kwargs.get("reservation_time")
        duration_minutes = kwargs.get("duration_minutes")
        table_id = kwargs.get("table_id")
        new_end_time = reservation_time + timedelta(minutes=duration_minutes)
        stmt = select(
            exists().where(
                Reservation.table_id == table_id,
                Reservation.reservation_time <= new_end_time,
                (
                    Reservation.reservation_time
                    + func.cast(
                        func.concat(Reservation.duration_minutes, " minutes"), INTERVAL
                    )
                )
                >= reservation_time,
            )
        )
        result = await db.execute(stmt)
        if result.scalar():
            raise HTTPException(
                status_code=400, detail="The reservation overlaps with another"
            )
        return await super().create(db, **kwargs)
