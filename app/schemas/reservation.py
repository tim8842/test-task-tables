from pydantic import BaseModel, conint
from datetime import datetime


class RequestCreateReservation(BaseModel):
    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: conint(ge=1)


class ResponseTable(RequestCreateReservation):
    id: int
