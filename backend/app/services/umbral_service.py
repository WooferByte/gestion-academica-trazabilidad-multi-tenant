import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.repositories.umbral_repository import UmbralMateriaRepository
from app.schemas.auth import UserContext
from app.schemas.umbral import UmbralMateriaResponse, UmbralMateriaUpdate
from app.services.audit_service import AuditService


class UmbralService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._umbral_repo = UmbralMateriaRepository(session, tenant_id)

    async def configurar_umbral(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        data: UmbralMateriaUpdate,
        current_user: UserContext,
        audit: AuditService,
    ) -> UmbralMateriaResponse:
        result = await self._session.execute(
            select(Asignacion)
            .where(Asignacion.usuario_id == current_user.user_id)
            .where(Asignacion.materia_id == materia_id)
            .where(Asignacion.tenant_id == self._tenant_id)
            .where(Asignacion.deleted_at.is_(None))
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=403,
                detail='No tienes una asignación activa para esta materia',
            )

        umbral = await self._umbral_repo.upsert(
            asignacion_id=asignacion.id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            umbral_pct=data.umbral_pct,
            valores_aprobatorios=data.valores_aprobatorios,
        )

        await audit.log(
            accion='CONFIGURAR_UMBRAL',
            detalle={
                'materia_id': str(materia_id),
                'cohorte_id': str(cohorte_id),
                'umbral_pct': data.umbral_pct,
                'valores_aprobatorios': data.valores_aprobatorios,
            },
            filas_afectadas=0,
            materia_id=materia_id,
        )

        return UmbralMateriaResponse.model_validate(umbral)

    async def obtener_umbral(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> UmbralMateriaResponse:
        umbral = await self._umbral_repo.get_by_materia_cohorte(materia_id, cohorte_id)
        if umbral:
            return UmbralMateriaResponse.model_validate(umbral)

        return UmbralMateriaResponse(
            id=uuid.uuid4(),
            tenant_id=self._tenant_id,
            asignacion_id=uuid.uuid4(),
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            umbral_pct=60,
            valores_aprobatorios=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
