from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import Integer, String, CheckConstraint
from ..database import Base
from .base import BaseDao


class Table(Base, BaseDao):
    __tablename__ = "tables"
    __table_args__ = (CheckConstraint("seats >= 0", name="check_seats_positive"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String)
    reservations = relationship("Reservation", back_populates="table")
