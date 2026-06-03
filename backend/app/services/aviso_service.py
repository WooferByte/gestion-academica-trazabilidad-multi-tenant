import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso
from app.repositories.aviso_repository import AvisoRepository
from app.schemas.aviso import (
    AckResponse,
    AvisoCreate,
    AvisoListResponse,
    AvisoResponse,
    AvisoUpdate,
)
from app.schemas.auth import UserContext


class AvisoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = AvisoRepository(session, tenant_id)

    async def crear(self, data: AvisoCreate, current_user: UserContext) -> AvisoResponse:
        aviso = await self._repo.create(
            alcance=data.alcance,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            rol_destino=data.rol_destino,
            severidad=data.severidad,
            titulo=data.titulo,
            cuerpo=data.cuerpo,
            inicio_vigencia=data.inicio_vigencia,
            fin_vigencia=data.fin_vigencia,
            orden=data.orden,
            requiere_ack=data.requiere_ack,
        )
        return self._to_response(aviso, current_user)

    async def actualizar(self, aviso_id: uuid.UUID, data: AvisoUpdate) -> AvisoResponse:
        aviso = await self._repo.get(aviso_id)
        if not aviso:
            raise HTTPException(status_code=404, detail='Aviso no encontrado')

        update_kwargs = data.model_dump(exclude_unset=True)
        aviso = await self._repo.update(aviso, **update_kwargs)
        return self._to_response(aviso)

    async def desactivar(self, aviso_id: uuid.UUID) -> dict:
        aviso = await self._repo.get(aviso_id)
        if not aviso:
            raise HTTPException(status_code=404, detail='Aviso no encontrado')
        await self._repo.update(aviso, activo=False)
        return {'detalle': 'Aviso desactivado'}

    async def listar_avisos_para_usuario(
        self, current_user: UserContext,
    ) -> AvisoListResponse:
        avisos = await self._repo.list_visibles(
            usuario_id=current_user.user_id,
            roles=current_user.roles,
        )
        items = [await self._build_response(a, current_user) for a in avisos]
        return AvisoListResponse(items=items, total=len(items))

    async def obtener_aviso(self, aviso_id: uuid.UUID, current_user: UserContext) -> AvisoResponse:
        aviso = await self._repo.get(aviso_id)
        if not aviso or not aviso.activo:
            raise HTTPException(status_code=404, detail='Aviso no encontrado')
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if aviso.inicio_vigencia > now or aviso.fin_vigencia < now:
            raise HTTPException(status_code=404, detail='Aviso no encontrado')
        return await self._build_response(aviso, current_user)

    async def confirmar_lectura(self, aviso_id: uuid.UUID, current_user: UserContext) -> AckResponse:
        aviso = await self._repo.get(aviso_id)
        if not aviso or not aviso.activo:
            raise HTTPException(status_code=404, detail='Aviso no encontrado')

        ya_ack = await self._repo.user_has_acked(aviso_id, current_user.user_id)
        if ya_ack:
            raise HTTPException(status_code=409, detail='Ya confirmaste este aviso')

        ack = await self._repo.create_ack(aviso_id, current_user.user_id)
        return AckResponse(
            id=ack.id,
            aviso_id=ack.aviso_id,
            usuario_id=ack.usuario_id,
            confirmado_at=ack.confirmado_at,
        )

    async def _build_response(self, aviso: Aviso, current_user: UserContext | None = None) -> AvisoResponse:
        total_acks = await self._repo.count_acks(aviso.id)
        user_acked = False
        if current_user:
            user_acked = await self._repo.user_has_acked(aviso.id, current_user.user_id)
        return self._to_response(aviso, current_user, total_acks, user_acked)

    def _to_response(
        self,
        aviso: Aviso,
        current_user: UserContext | None = None,
        total_acks: int = 0,
        user_acked: bool = False,
    ) -> AvisoResponse:
        return AvisoResponse(
            id=aviso.id,
            tenant_id=aviso.tenant_id,
            alcance=aviso.alcance.value if hasattr(aviso.alcance, 'value') else str(aviso.alcance),
            materia_id=aviso.materia_id,
            cohorte_id=aviso.cohorte_id,
            rol_destino=aviso.rol_destino,
            severidad=aviso.severidad.value if hasattr(aviso.severidad, 'value') else str(aviso.severidad),
            titulo=aviso.titulo,
            cuerpo=aviso.cuerpo,
            inicio_vigencia=aviso.inicio_vigencia,
            fin_vigencia=aviso.fin_vigencia,
            orden=aviso.orden,
            activo=aviso.activo,
            requiere_ack=aviso.requiere_ack,
            total_acks=total_acks,
            user_acked=user_acked,
            created_at=aviso.created_at,
            updated_at=aviso.updated_at,
        )
