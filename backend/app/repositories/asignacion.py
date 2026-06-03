import uuid
from collections.abc import Sequence

from sqlalchemy import select

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