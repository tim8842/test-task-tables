from fastapi import APIRouter, Depends, Path
from ..models.table import Table
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.table import RequestCreateTable

router = APIRouter()


@router.get("")
async def get_all_tables(db: AsyncSession = Depends(get_db)):
    tables = await Table.getAll(db)
    return {"tables": tables}


@router.post("")
async def create_table(table: RequestCreateTable, db: AsyncSession = Depends(get_db)):
    table = table.model_dump()
    table = await Table.create(db, **table)
    return {"table": table}


@router.delete("/{id}")
async def delete_table(id: int = Path(...), db: AsyncSession = Depends(get_db)):
    table = await Table.deleteById(db, id)
    return {"table": table}
