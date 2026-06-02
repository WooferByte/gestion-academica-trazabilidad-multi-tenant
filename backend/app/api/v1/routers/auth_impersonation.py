import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_codes import IMPERSONACION_FINALIZAR, IMPERSONACION_INICIAR
from app.core.audit_dependency import get_audit_service
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse, UserContext
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService

router = APIRouter(prefix='/api/v1/auth')


class ImpersonateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    target_user_id: uuid.UUID


@router.post('/impersonate')
async def impersonate(
    body: ImpersonateRequest,
    request: Request,
    _: None = require_permission('impersonacion:usar'),
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
):
    if body.target_user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail='No puedes impersonarte a ti mismo')

    user_repo = UserRepository(db, current_user.tenant_id)
    target = await user_repo.get(body.target_user_id)
    if not target:
        raise HTTPException(status_code=404, detail='Usuario destino no encontrado')

    svc = AuthService(db, current_user.tenant_id)
    session = await svc.create_session(target)

    access_token = create_access_token(
        user_id=str(target.id),
        tenant_id=str(target.tenant_id),
        roles=target.roles,
        impersonator_id=str(current_user.user_id),
    )

    await audit.log(
        accion=IMPERSONACION_INICIAR,
        detalle={'target_user_id': str(target.id), 'target_email': target.email},
        filas_afectadas=1,
        ip=request.client.host if request.client else 'unknown',
        user_agent=request.headers.get('user-agent', 'unknown'),
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=session['refresh_token'],
        token_type='bearer',
        expires_in=session['expires_in'],
    )


@router.post('/impersonate/stop')
async def impersonate_stop(
    request: Request,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
):
    if current_user.impersonator_id is None:
        raise HTTPException(status_code=400, detail='No hay una impersonación activa')

    user_repo = UserRepository(db, current_user.tenant_id)
    impersonator = await user_repo.get(current_user.impersonator_id)
    if not impersonator:
        raise HTTPException(
            status_code=400,
            detail='El usuario impersonador ya no existe',
        )

    svc = AuthService(db, current_user.tenant_id)
    session = await svc.create_session(impersonator)

    await audit.log(
        accion=IMPERSONACION_FINALIZAR,
        detalle={'impersonated_user_id': str(current_user.user_id)},
        filas_afectadas=1,
        ip=request.client.host if request.client else 'unknown',
        user_agent=request.headers.get('user-agent', 'unknown'),
    )

    return LoginResponse(
        access_token=session['access_token'],
        refresh_token=session['refresh_token'],
        token_type='bearer',
        expires_in=session['expires_in'],
    )
