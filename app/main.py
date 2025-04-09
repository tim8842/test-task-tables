from fastapi import FastAPI
from .routers.table import router as table_router
from .routers.reservation import router as reservation_router

app = FastAPI()
app.include_router(
    table_router,
    prefix="/api/v1/tables",
    tags=["tables"],
)
app.include_router(
    reservation_router, prefix="/api/v1/reservations", tags=["reservations"]
)
# app.include_router(components_router, prefix="/api/v1/components", tags=["components"])
