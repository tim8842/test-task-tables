from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from sqlalchemy.future import select
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class IBaseDao(ABC):
    @abstractmethod
    def getAll(cls, db: AsyncSession):
        pass

    @abstractmethod
    def getById(cls, db: AsyncSession, id: int):
        pass

    @abstractmethod
    def create(cls, db: AsyncSession, **kwargs):
        pass

    @abstractmethod
    def deleteById(cls, db: AsyncSession, id: int):
        pass


class BaseDao(IBaseDao):
    id: int

    @classmethod
    async def getAll(cls, db: AsyncSession) -> List["BaseDao"]:
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def getById(cls, db: AsyncSession, id: int) -> Optional["BaseDao"]:
        return (await db.execute(select(cls).where(cls.id == id))).scalar_one_or_none()

    @classmethod
    async def deleteById(cls, db: AsyncSession, id: int) -> "BaseDao":
        item = await cls.getById(db, id)
        if item:
            await db.delete(item)
            await db.commit()
            return item
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Table with ID {id} not found.")

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> "BaseDao":
        try:
            new_object = cls(**kwargs)
            db.add(new_object)
            await db.commit()
            return new_object
        except IntegrityError as e:
            await db.rollback()
            if hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
                raise HTTPException(
                    status_code=400, detail=f"foreign key error: no table with such id"
                )
