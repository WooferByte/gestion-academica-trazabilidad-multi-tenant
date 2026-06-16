"""
# Transición user_roles ↔ asignacion

Durante la coexistencia (C-07 a C-08), `user_roles` y `asignaciones` conviven:
- `user_roles` (C-04) mantiene el vínculo legacy usuario ↔ rol para claims JWT rápidos.
- `asignaciones` (C-07) es el nuevo modelo que agrega contexto académico (materia, carrera,
  cohorte, comisiones, responsable) con vigencia temporal.

**En un change futuro `asignacion` prevalece como fuente única** y `user_roles`
se depreca. Hasta entonces, ambos sistemas coexisten y deben mantenerse sincronizados
cuando se creen/modifiquen asignaciones que impliquen un cambio de rol.
"""
import csv
import io
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_codes import ASIGNACION_MODIFICAR
from app.core.security import decrypt
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.user import User
from app.repositories.asignacion import AsignacionRepository
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionListResponse,
    AsignacionResponse,
    AsignacionUpdate,
)
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService


def _rangos_se_superponen(d1, h1, d2, h2):
    if not d1 or not d2:
        return False
    return d1 < h2 and d2 < h1


class AsignacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = AsignacionRepository(session, tenant_id)
        self._tenant_id = tenant_id

    async def list_asignaciones(
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
    ) -> dict:
        asignaciones = await self._repo.list_with_filters(
            usuario_id=usuario_id,
            rol=rol,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            responsable_id=responsable_id,
            solo_vigentes=solo_vigentes,
            skip=skip,
            limit=limit,
        )
        return {
            'items': [await self._to_response(a) for a in asignaciones],
            'total': len(asignaciones),
        }

    async def get_asignacion(self, asignacion_id: uuid.UUID) -> dict:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        return await self._to_response(asignacion)

    async def create_asignacion(self, data: AsignacionCreate) -> dict:
        await self._validar_no_solapamiento(
            usuario_id=data.usuario_id,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            desde=data.desde,
            hasta=data.hasta,
        )
        asignacion = await self._repo.create(**data.model_dump())
        return await self._to_response(asignacion)

    async def update_asignacion(
        self, asignacion_id: uuid.UUID, data: AsignacionUpdate,
    ) -> dict:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return await self._to_response(asignacion)

        if any(k in update_data for k in ('materia_id', 'cohorte_id', 'desde', 'hasta')):
            await self._validar_no_solapamiento(
                usuario_id=update_data.get('usuario_id', asignacion.usuario_id),
                materia_id=update_data.get('materia_id', asignacion.materia_id),
                cohorte_id=update_data.get('cohorte_id', asignacion.cohorte_id),
                desde=update_data.get('desde', asignacion.desde),
                hasta=update_data.get('hasta', asignacion.hasta),
                excluir_id=asignacion.id,
            )

        updated = await self._repo.update(asignacion, **update_data)
        return await self._to_response(updated)

    async def delete_asignacion(self, asignacion_id: uuid.UUID) -> None:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        await self._repo.soft_delete(asignacion)

    async def mis_equipos(
        self,
        usuario_id: uuid.UUID,
        *,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        solo_vigentes: bool = False,
    ) -> dict:
        asignaciones = await self._repo.list_with_filters(
            usuario_id=usuario_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            solo_vigentes=solo_vigentes,
        )
        return {
            'items': [await self._to_response(a) for a in asignaciones],
            'total': len(asignaciones),
        }

    async def asignacion_masiva(
        self,
        data,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> list[dict]:
        usuario_ids = data.usuario_ids
        result = await self._session.execute(
            select(User).where(
                User.id.in_(usuario_ids),
                User.tenant_id == self._tenant_id,
                User.deleted_at.is_(None),
            ),
        )
        existing = {u.id for u in result.scalars().all()}
        missing = [str(uid) for uid in usuario_ids if uid not in existing]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f'Usuarios no encontrados: {", ".join(missing)}',
            )

        entries = [
            {
                'usuario_id': uid,
                'rol': data.rol,
                'materia_id': data.materia_id,
                'carrera_id': data.carrera_id,
                'cohorte_id': data.cohorte_id,
                'comisiones': data.comisiones,
                'responsable_id': data.responsable_id,
                'desde': data.desde,
                'hasta': data.hasta,
            }
            for uid in usuario_ids
        ]
        asignaciones = await self._repo.create_bulk(entries)

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=ASIGNACION_MODIFICAR,
            detalle={
                'tipo': 'asignacion_masiva',
                'usuario_ids': [str(uid) for uid in usuario_ids],
                'materia_id': str(data.materia_id) if data.materia_id else None,
                'cohorte_id': str(data.cohorte_id) if data.cohorte_id else None,
                'rol': data.rol,
            },
            filas_afectadas=len(asignaciones),
        )

        return [await self._to_response(a) for a in asignaciones]

    async def clonar_equipo(
        self,
        data,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> list[dict]:
        creadas = await self._repo.clone_vigentes(
            origen=data.origen.model_dump(),
            destino=data.destino.model_dump(),
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=ASIGNACION_MODIFICAR,
            detalle={
                'tipo': 'clonar_equipo',
                'origen': data.origen.model_dump(mode='json'),
                'destino': data.destino.model_dump(mode='json'),
            },
            filas_afectadas=len(creadas),
        )

        return [await self._to_response(a) for a in creadas]

    async def modificar_vigencia(
        self,
        data,
        current_user: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ) -> dict:
        existentes = await self._repo.list_with_filters(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
        )
        if not existentes:
            raise HTTPException(
                status_code=404,
                detail='No existen asignaciones para el equipo especificado',
            )

        filas = await self._repo.update_vigencia_bulk(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            desde=data.desde,
            hasta=data.hasta,
        )

        audit = AuditService(self._session, current_user, ip, user_agent)
        await audit.log(
            accion=ASIGNACION_MODIFICAR,
            detalle={
                'tipo': 'modificar_vigencia',
                'materia_id': str(data.materia_id),
                'carrera_id': str(data.carrera_id),
                'cohorte_id': str(data.cohorte_id),
            },
            filas_afectadas=filas,
        )

        return {'filas_afectadas': filas}

    async def exportar_equipo(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
    ) -> str:
        from app.core.security import decrypt

        asignaciones = await self._repo.list_for_export(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
        )

        user_ids = list({a.usuario_id for a in asignaciones if a.usuario_id})
        users_map: dict[uuid.UUID, User] = {}
        if user_ids:
            result = await self._session.execute(
                select(User).where(User.id.in_(user_ids)),
            )
            users_map = {u.id: u for u in result.scalars().all()}

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'docente', 'email', 'rol', 'materia_id',
            'carrera_id', 'cohorte_id', 'comisiones', 'desde', 'hasta',
        ])

        for a in asignaciones:
            user = users_map.get(a.usuario_id) if a.usuario_id else None
            nombre = ''
            if user and user.nombre_cifrado:
                try:
                    nombre = decrypt(user.nombre_cifrado)
                except Exception:
                    nombre = ''
            apellido = ''
            if user and user.apellido_cifrado:
                try:
                    apellido = decrypt(user.apellido_cifrado)
                except Exception:
                    apellido = ''
            docente = f'{nombre} {apellido}'.strip()
            writer.writerow([
                docente,
                user.email if user else '',
                a.rol or '',
                str(a.materia_id) if a.materia_id else '',
                str(a.carrera_id) if a.carrera_id else '',
                str(a.cohorte_id) if a.cohorte_id else '',
                ','.join(a.comisiones or []),
                a.desde.isoformat() if a.desde else '',
                a.hasta.isoformat() if a.hasta else '',
            ])

        return output.getvalue()

    async def _validar_no_solapamiento(
        self,
        usuario_id: uuid.UUID,
        materia_id: uuid.UUID | None,
        cohorte_id: uuid.UUID | None,
        desde: datetime | None,
        hasta: datetime | None,
        excluir_id: uuid.UUID | None = None,
    ):
        stmt = select(self._repo._model).where(
            self._repo._model.tenant_id == self._tenant_id,
            self._repo._model.deleted_at.is_(None),
            self._repo._model.usuario_id == usuario_id,
            self._repo._model.materia_id == materia_id,
            self._repo._model.cohorte_id == cohorte_id,
        )
        if excluir_id:
            stmt = stmt.where(self._repo._model.id != excluir_id)

        result = await self._session.execute(stmt)
        existentes = result.scalars().all()

        for existente in existentes:
            if _rangos_se_superponen(existente.desde, existente.hasta, desde, hasta):
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f'VAL-01: El docente ya tiene una asignación en '
                        f'{materia_id}/{cohorte_id} cuyas fechas '
                        f'{existente.desde} a {existente.hasta} se superponen '
                        f'con el período solicitado {desde} a {hasta}'
                    ),
                )

    async def _resolve_nombre_usuario(self, usuario_id: uuid.UUID) -> str:
        result = await self._session.execute(
            select(User).where(User.id == usuario_id, User.tenant_id == self._tenant_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return str(usuario_id)
        nombre = decrypt(user.nombre_cifrado) if user.nombre_cifrado else ''
        apellido = decrypt(user.apellido_cifrado) if user.apellido_cifrado else ''
        return f"{nombre} {apellido}".strip() or str(usuario_id)

    async def _resolve_nombre_materia(self, materia_id: uuid.UUID | None) -> str | None:
        if not materia_id:
            return None
        result = await self._session.execute(
            select(Materia).where(Materia.id == materia_id, Materia.tenant_id == self._tenant_id)
        )
        materia = result.scalar_one_or_none()
        return materia.nombre if materia else None

    async def _resolve_nombre_carrera(self, carrera_id: uuid.UUID | None) -> str | None:
        if not carrera_id:
            return None
        result = await self._session.execute(
            select(Carrera).where(Carrera.id == carrera_id, Carrera.tenant_id == self._tenant_id)
        )
        carrera = result.scalar_one_or_none()
        return carrera.nombre if carrera else None

    async def _resolve_nombre_cohorte(self, cohorte_id: uuid.UUID | None) -> str | None:
        if not cohorte_id:
            return None
        result = await self._session.execute(
            select(Cohorte).where(Cohorte.id == cohorte_id, Cohorte.tenant_id == self._tenant_id)
        )
        cohorte = result.scalar_one_or_none()
        return cohorte.nombre if cohorte else None

    async def _to_response(self, asignacion) -> dict:
        usuario_nombre = await self._resolve_nombre_usuario(asignacion.usuario_id)
        materia_nombre = await self._resolve_nombre_materia(asignacion.materia_id)
        carrera_nombre = await self._resolve_nombre_carrera(asignacion.carrera_id)
        cohorte_nombre = await self._resolve_nombre_cohorte(asignacion.cohorte_id)
        return AsignacionResponse(
            id=asignacion.id,
            tenant_id=asignacion.tenant_id,
            usuario_id=asignacion.usuario_id,
            usuario_nombre=usuario_nombre,
            rol=asignacion.rol,
            materia_id=asignacion.materia_id,
            materia_nombre=materia_nombre,
            carrera_id=asignacion.carrera_id,
            carrera_nombre=carrera_nombre,
            cohorte_id=asignacion.cohorte_id,
            cohorte_nombre=cohorte_nombre,
            comisiones=asignacion.comisiones,
            responsable_id=asignacion.responsable_id,
            desde=asignacion.desde,
            hasta=asignacion.hasta,
            created_at=asignacion.created_at,
            updated_at=asignacion.updated_at,
            deleted_at=asignacion.deleted_at,
        )