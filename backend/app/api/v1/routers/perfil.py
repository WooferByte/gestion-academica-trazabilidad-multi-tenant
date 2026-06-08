from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import UserContext
from app.schemas.perfil import PerfilResponse, PerfilUpdate
from app.services.perfil import PerfilService

router = APIRouter(prefix='/api/v1/perfil')


@router.get('', response_model=PerfilResponse)
async def get_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> PerfilResponse:
    svc = PerfilService(db, current_user.tenant_id)
    return await svc.get_profile(current_user.user_id)


@router.put('', response_model=PerfilResponse)
async def update_perfil(
    body: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> PerfilResponse:
    svc = PerfilService(db, current_user.tenant_id)
    return await svc.update_profile(current_user.user_id, body)
