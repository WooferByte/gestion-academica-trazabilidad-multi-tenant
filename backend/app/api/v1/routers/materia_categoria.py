import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.categoria_plus import CategoriaPlusRepository
from app.repositories.materia import MateriaRepository
from app.schemas.auth import UserContext
from app.schemas.categoria_plus import (AsignarCategoriaRequest,
                                         CategoriaPlusResponse)
from app.schemas.materia import MateriaResponse

router = APIRouter(prefix='/api/v1/admin/materias/{materia_id}/categoria', tags=['materias-categoria'])


@router.get('')
async def get_categoria_de_materia(
    materia_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    materia_repo = MateriaRepository(session, current_user.tenant_id)
    materia = await materia_repo.get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail='Materia no encontrada')
    if not materia.categoria_plus_id:
        return {'data': None}
    cat_repo = CategoriaPlusRepository(session, current_user.tenant_id)
    categoria = await cat_repo.get(materia.categoria_plus_id)
    if not categoria:
        return {'data': None}
    return {'data': CategoriaPlusResponse.model_validate(categoria).model_dump(mode='json')}


@router.put('', response_model=MateriaResponse)
async def assign_categoria_a_materia(
    materia_id: uuid.UUID,
    data: AsignarCategoriaRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> MateriaResponse:
    materia_repo = MateriaRepository(session, current_user.tenant_id)
    materia = await materia_repo.get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail='Materia no encontrada')
    cat_repo = CategoriaPlusRepository(session, current_user.tenant_id)
    categoria = await cat_repo.get(data.categoria_plus_id)
    if not categoria:
        raise HTTPException(status_code=404, detail='Categoría no encontrada')
    materia.categoria_plus_id = data.categoria_plus_id
    await session.flush()
    await session.refresh(materia)
    return MateriaResponse.model_validate(materia)


@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
async def unassign_categoria_de_materia(
    materia_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    materia_repo = MateriaRepository(session, current_user.tenant_id)
    materia = await materia_repo.get(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail='Materia no encontrada')
    materia.categoria_plus_id = None
    await session.flush()
