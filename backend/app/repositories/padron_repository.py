import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository


class VersionPadronRepository(BaseRepository[VersionPadron]):
    __model__ = VersionPadron

    async def get_activa(self, materia_id: uuid.UUID, cohorte_id: uuid.UUID) -> VersionPadron | None:
        stmt = (
            self._stmt()
            .where(VersionPadron.materia_id == materia_id)
            .where(VersionPadron.cohorte_id == cohorte_id)
            .where(VersionPadron.activa.is_(True))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def desactivar_version(self, version_id: uuid.UUID) -> None:
        stmt = (
            update(VersionPadron)
            .where(VersionPadron.id == version_id)
            .where(VersionPadron.tenant_id == self._tenant_id)
            .values(activa=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()


class EntradaPadronRepository(BaseRepository[EntradaPadron]):
    __model__ = EntradaPadron

    async def get_by_version(self, version_id: uuid.UUID) -> Sequence[EntradaPadron]:
        stmt = self._stmt().where(EntradaPadron.version_id == version_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def bulk_create(self, version_id: uuid.UUID, entradas: list[dict]) -> list[EntradaPadron]:
        instances = []
        for data in entradas:
            instance = EntradaPadron(
                tenant_id=self._tenant_id,
                version_id=version_id,
                usuario_id=data.get('usuario_id'),
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                email=data['email'],
                comision=data['comision'],
                regional=data['regional'],
            )
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances

    async def soft_delete_by_version(self, version_id: uuid.UUID) -> int:
        from datetime import datetime, timezone

        stmt = (
            select(EntradaPadron)
            .where(EntradaPadron.version_id == version_id)
            .where(EntradaPadron.tenant_id == self._tenant_id)
            .where(EntradaPadron.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        entradas = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        for e in entradas:
            e.deleted_at = now
        await self._session.flush()
        return len(entradas)
