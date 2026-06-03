import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.usuario import UsuarioCreate, UsuarioListResponse, UsuarioResponse, UsuarioUpdate
from app.services.usuario import UsuarioService

router = APIRouter(prefix='/api/v1/admin/usuarios', tags=['usuarios'])


@router.get('', response_model=UsuarioListResponse)
async def list_usuarios(
    estado: str | None = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('usuarios:gestionar'),
):
    service = UsuarioService(session, current_user.tenant_id)
    return await service.list_usuarios(estado=estado, skip=skip, limit=limit)


@router.post('', response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    data: UsuarioCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('usuarios:gestionar'),
):
    service = UsuarioService(session, current_user.tenant_id)
    return await service.create_usuario(data)


@router.get('/{usuario_id}', response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('usuarios:gestionar'),
):
    service = UsuarioService(session, current_user.tenant_id)
    return await service.get_usuario(usuario_id)


@router.patch('/{usuario_id}', response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: uuid.UUID,
    data: UsuarioUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('usuarios:gestionar'),
):
    service = UsuarioService(session, current_user.tenant_id)
    return await service.update_usuario(usuario_id, data)


@router.delete('/{usuario_id}', status_code=status.HTTP_200_OK)
async def delete_usuario(
    usuario_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('usuarios:gestionar'),
):
    service = UsuarioService(session, current_user.tenant_id)
    await service.delete_usuario(usuario_id)
    return {'detail': 'Usuario desactivado'}