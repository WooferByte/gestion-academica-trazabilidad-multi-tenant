import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_codes import COMUNICACION_ENVIAR
from app.core.security import encrypt
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.tenant import Tenant
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.schemas.comunicacion import (
    ComunicacionCreate,
    ComunicacionListResponse,
    ComunicacionPreviewRequest,
    ComunicacionPreviewResponse,
    ComunicacionResponse,
)
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService

VARIABLE_PATTERN = re.compile(r'\{\{(\w+(?:\.\w+)*)\}\}')


def _render_template(text: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    not_found: list[str] = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        value = variables.get(key)
        if value is not None:
            return value
        not_found.append(key)
        return ''

    result = VARIABLE_PATTERN.sub(_replace, text)
    return result, not_found


class ComunicacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = ComunicacionRepository(session, tenant_id)
        self._tenant_id = tenant_id

    async def preview(self, data: ComunicacionPreviewRequest) -> ComunicacionPreviewResponse:
        asunto_render, asunto_not_found = _render_template(data.asunto, data.variables)
        cuerpo_render, cuerpo_not_found = _render_template(data.cuerpo, data.variables)
        all_not_found = list(set(asunto_not_found + cuerpo_not_found))
        return ComunicacionPreviewResponse(
            asunto_renderizado=asunto_render,
            cuerpo_renderizado=cuerpo_render,
            variables_no_encontradas=all_not_found,
        )

    async def encolar(
        self,
        data: ComunicacionCreate,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> ComunicacionResponse:
        destinatario_cifrado = encrypt(data.destinatario)
        requiere_aprobacion = await self._tenant_requiere_aprobacion()
        lote_id = uuid.uuid4()

        comunicacion = await self._repo.create(
            enviado_por=current_user.user_id,
            materia_id=data.materia_id,
            destinatario=destinatario_cifrado,
            asunto=data.asunto,
            cuerpo=data.cuerpo,
            estado=EstadoComunicacion.PENDIENTE,
            lote_id=lote_id,
            aprobacion_requerida=requiere_aprobacion,
            programada_para=data.programada_para,
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=COMUNICACION_ENVIAR,
            detalle={
                'tipo': 'encolar_individual',
                'comunicacion_id': str(comunicacion.id),
                'lote_id': str(lote_id),
                'materia_id': str(data.materia_id) if data.materia_id else None,
                'aprobacion_requerida': requiere_aprobacion,
            },
            filas_afectadas=1,
            materia_id=data.materia_id,
        )

        return self._to_response(comunicacion, descifrar=False)

    async def encolar_lote(
        self,
        data,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> list[ComunicacionResponse]:
        requiere_aprobacion = await self._tenant_requiere_aprobacion()
        lote_id = uuid.uuid4()
        creadas: list[Comunicacion] = []

        for destinatario in data.destinatarios:
            destinatario_cifrado = encrypt(destinatario)
            c = await self._repo.create(
                enviado_por=current_user.user_id,
                materia_id=data.materia_id,
                destinatario=destinatario_cifrado,
                asunto=data.asunto,
                cuerpo=data.cuerpo,
                estado=EstadoComunicacion.PENDIENTE,
                lote_id=lote_id,
                aprobacion_requerida=requiere_aprobacion,
                programada_para=data.programada_para,
            )
            creadas.append(c)

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=COMUNICACION_ENVIAR,
            detalle={
                'tipo': 'encolar_lote',
                'lote_id': str(lote_id),
                'cantidad': len(data.destinatarios),
                'materia_id': str(data.materia_id) if data.materia_id else None,
                'aprobacion_requerida': requiere_aprobacion,
            },
            filas_afectadas=len(creadas),
            materia_id=data.materia_id,
        )

        return [self._to_response(c, descifrar=False) for c in creadas]

    async def aprobar_lote(
        self,
        lote_id: uuid.UUID,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> dict:
        comunicaciones = await self._repo.get_by_lote(lote_id)
        if not comunicaciones:
            raise HTTPException(status_code=404, detail='Lote no encontrado')

        afectadas = await self._repo.update_estado_by_lote(
            lote_id=lote_id,
            estado=EstadoComunicacion.PENDIENTE,
            aprobada_por=current_user.user_id,
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=COMUNICACION_ENVIAR,
            detalle={
                'tipo': 'aprobar_lote',
                'lote_id': str(lote_id),
                'accion': 'aprobar',
            },
            filas_afectadas=afectadas,
        )

        return {'detalle': 'Lote aprobado', 'filas_afectadas': afectadas}

    async def rechazar_lote(
        self,
        lote_id: uuid.UUID,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> dict:
        comunicaciones = await self._repo.get_by_lote(lote_id)
        if not comunicaciones:
            raise HTTPException(status_code=404, detail='Lote no encontrado')

        afectadas = await self._repo.update_estado_by_lote(
            lote_id=lote_id,
            estado=EstadoComunicacion.CANCELADO,
            cancelada_por=current_user.user_id,
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=COMUNICACION_ENVIAR,
            detalle={
                'tipo': 'rechazar_lote',
                'lote_id': str(lote_id),
                'accion': 'rechazar',
            },
            filas_afectadas=afectadas,
        )

        return {'detalle': 'Lote rechazado', 'filas_afectadas': afectadas}

    async def cancelar(
        self,
        comunicacion_id: uuid.UUID,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> dict:
        comunicacion = await self._repo.get(comunicacion_id)
        if not comunicacion:
            raise HTTPException(status_code=404, detail='Comunicación no encontrada')

        if comunicacion.estado not in (EstadoComunicacion.PENDIENTE,):
            raise HTTPException(
                status_code=400,
                detail=f'No se puede cancelar una comunicación en estado {comunicacion.estado.value}',
            )

        await self._repo.update_estado(
            comunicacion_id=comunicacion_id,
            estado=EstadoComunicacion.CANCELADO,
            cancelada_por=current_user.user_id,
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=COMUNICACION_ENVIAR,
            detalle={
                'tipo': 'cancelar',
                'comunicacion_id': str(comunicacion_id),
            },
            filas_afectadas=1,
        )

        return {'detalle': 'Comunicación cancelada'}

    async def listar_por_lote(
        self,
        lote_id: uuid.UUID,
        current_user: UserContext,
    ) -> ComunicacionListResponse:
        comunicaciones = await self._repo.get_by_lote(lote_id)
        owner = comunicaciones[0].enviado_por if comunicaciones else None
        descifrar = owner is not None and current_user.user_id == owner
        items = [self._to_response(c, descifrar=descifrar) for c in comunicaciones]
        return ComunicacionListResponse(items=items, total=len(items))

    async def listar_por_materia(
        self,
        materia_id: uuid.UUID,
        _current_user: UserContext,
    ) -> ComunicacionListResponse:
        comunicaciones = await self._repo.get_by_materia(materia_id)
        return ComunicacionListResponse(
            items=[self._to_response(c) for c in comunicaciones],
            total=len(comunicaciones),
        )

    async def _tenant_requiere_aprobacion(self) -> bool:
        from sqlalchemy import select
        result = await self._session.execute(
            select(Tenant.aprobacion_comunicaciones).where(Tenant.id == self._tenant_id),
        )
        row = result.scalar_one_or_none()
        return bool(row)

    def _to_response(self, c: Comunicacion, descifrar: bool = True) -> ComunicacionResponse:
        destinatario = c.destinatario
        if descifrar:
            try:
                from app.core.security import decrypt
                destinatario = decrypt(c.destinatario)
            except Exception:
                pass

        return ComunicacionResponse(
            id=c.id,
            tenant_id=c.tenant_id,
            enviado_por=c.enviado_por,
            materia_id=c.materia_id,
            destinatario=destinatario,
            asunto=c.asunto,
            cuerpo=c.cuerpo,
            estado=c.estado.value if isinstance(c.estado, EstadoComunicacion) else str(c.estado),
            lote_id=c.lote_id,
            aprobacion_requerida=c.aprobacion_requerida,
            error_msg=c.error_msg,
            programada_para=c.programada_para,
            enviada_at=c.enviada_at,
            aprobada_por=c.aprobada_por,
            cancelada_por=c.cancelada_por,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
