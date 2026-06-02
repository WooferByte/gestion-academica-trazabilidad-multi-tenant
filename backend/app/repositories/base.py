import uuid
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SoftDeletedException
from app.models.mixins import BaseModelMixin


class BaseRepository[T: BaseModelMixin]:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    @property
    def _model(self) -> type[T]:
        model = getattr(self.__class__, '__model__', None)
        if model is None:
            msg = f'{self.__class__.__name__} must define __model__'
            raise NotImplementedError(msg)
        return model

    def _stmt(self) -> Select:
        return (
            select(self._model)
            .where(self._model.tenant_id == self._tenant_id)
            .where(self._model.deleted_at.is_(None))
        )

    def _stmt_with_deleted(self) -> Select:
        return select(self._model).where(self._model.tenant_id == self._tenant_id)

    async def get(self, id: uuid.UUID) -> T | None:
        stmt = self._stmt().where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_deleted(self, id: uuid.UUID) -> T | None:
        stmt = self._stmt_with_deleted().where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = self._stmt().offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        kwargs['tenant_id'] = self._tenant_id
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def update(self, db_obj: T, **kwargs) -> T:
        if db_obj.deleted_at is not None:
            raise SoftDeletedException()
        for field, value in kwargs.items():
            setattr(db_obj, field, value)
        await self._session.flush()
        await self._session.refresh(db_obj)
        return db_obj

    async def soft_delete(self, db_obj: T) -> T:
        from datetime import datetime, timezone
        db_obj.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()
        return db_obj

    async def exists(self, **kwargs) -> bool:
        stmt = self._stmt()
        for field, value in kwargs.items():
            stmt = stmt.where(getattr(self._model, field) == value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
