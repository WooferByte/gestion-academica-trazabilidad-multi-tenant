import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select, update

from app.models.asignacion import Asignacion
from app.repositories.base import BaseRepository


class AsignacionRepository(BaseRepository[Asignacion]):
    __model__ = Asignacion

    async def list_with_filters(
        self,
        *,
        usuario_id: uuid.UUID | None = None,
        rol: str | None = None,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        responsable_id: uuid.UUID | None = None,
        solo_vigentes: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Asignacion]:
        stmt = self._stmt()
        if usuario_id is not None:
            stmt = stmt.where(Asignacion.usuario_id == usuario_id)
        if rol is not None:
            stmt = stmt.where(Asignacion.rol == rol)
        if materia_id is not None:
            stmt = stmt.where(Asignacion.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Asignacion.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Asignacion.cohorte_id == cohorte_id)
        if responsable_id is not None:
            stmt = stmt.where(Asignacion.responsable_id == responsable_id)
        if solo_vigentes:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            stmt = stmt.where(
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= now),
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_bulk(self, entries: list[dict]) -> list[Asignacion]:
        instances: list[Asignacion] = []
        for entry in entries:
            entry['tenant_id'] = self._tenant_id
            instance = self._model(**entry)
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances

    async def clone_vigentes(
        self,
        origen: dict,
        destino: dict,
    ) -> list[Asignacion]:
        vigentes = await self.list_with_filters(
            materia_id=origen.get('materia_id'),
            carrera_id=origen.get('carrera_id'),
            cohorte_id=origen.get('cohorte_id'),
            solo_vigentes=True,
        )
        if not vigentes:
            return []

        entries = []
        for v in vigentes:
            entries.append({
                'usuario_id': v.usuario_id,
                'rol': v.rol,
                'materia_id': destino.get('materia_id'),
                'carrera_id': destino.get('carrera_id'),
                'cohorte_id': destino.get('cohorte_id'),
                'comisiones': v.comisiones,
                'responsable_id': v.responsable_id,
                'desde': destino.get('desde'),
                'hasta': destino.get('hasta'),
            })
        return await self.create_bulk(entries)

    async def update_vigencia_bulk(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> int:
        valores = {}
        if desde is not None:
            valores['desde'] = desde
        if hasta is not None:
            valores['hasta'] = hasta
        if not valores:
            return 0

        stmt = (
            update(Asignacion)
            .where(Asignacion.tenant_id == self._tenant_id)
            .where(Asignacion.deleted_at.is_(None))
            .where(Asignacion.materia_id == materia_id)
            .where(Asignacion.carrera_id == carrera_id)
            .where(Asignacion.cohorte_id == cohorte_id)
            .values(**valores)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def list_for_export(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
    ) -> Sequence[Asignacion]:
        stmt = self._stmt()
        if materia_id is not None:
            stmt = stmt.where(Asignacion.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Asignacion.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Asignacion.cohorte_id == cohorte_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()