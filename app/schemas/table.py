from pydantic import BaseModel, conint


class RequestCreateTable(BaseModel):
    name: str
    seats: conint(ge=0)
    location: str


class ResponseTable(RequestCreateTable):
    id: int
