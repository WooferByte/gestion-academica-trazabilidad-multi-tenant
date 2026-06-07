import uuid
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.categoria_plus import CategoriaPlusRepository
from app.repositories.materia import MateriaRepository
from app.schemas.categoria_plus import (CategoriaPlusCreate,
                                         CategoriaPlusResponse,
                                         CategoriaPlusUpdate)
from app.schemas.materia import MateriaResponse


class CategoriaPlusService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._repo = CategoriaPlusRepository(session, tenant_id)
        self._materia_repo = MateriaRepository(session, tenant_id)

    async def list(self) -> dict:
        categorias = await self._repo.get_multi()
        return {
            'items': [CategoriaPlusResponse.model_validate(c) for c in categorias],
            'total': len(categorias),
        }

    async def get(self, categoria_id: uuid.UUID) -> CategoriaPlusResponse:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        return CategoriaPlusResponse.model_validate(categoria)

    async def create(self, data: CategoriaPlusCreate) -> CategoriaPlusResponse:
        existing = await self._repo.get_by_codigo(data.codigo)
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe una categoría con ese código')
        categoria = await self._repo.create(**data.model_dump())
        return CategoriaPlusResponse.model_validate(categoria)

    async def update(self, categoria_id: uuid.UUID, data: CategoriaPlusUpdate) -> CategoriaPlusResponse:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return CategoriaPlusResponse.model_validate(categoria)
        if 'codigo' in update_data:
            existing = await self._repo.get_by_codigo(update_data['codigo'])
            if existing and existing.id != categoria_id:
                raise HTTPException(status_code=409, detail='Ya existe una categoría con ese código')
        updated = await self._repo.update(categoria, **update_data)
        return CategoriaPlusResponse.model_validate(updated)

    async def delete(self, categoria_id: uuid.UUID) -> None:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        materias_count = await self._materia_repo.count_by_categoria(categoria_id)
        if materias_count > 0:
            raise HTTPException(
                status_code=409,
                detail=f'No se puede eliminar la categoría porque tiene {materias_count} materias asignadas',
            )
        await self._repo.soft_delete(categoria)

    async def toggle(self, categoria_id: uuid.UUID) -> CategoriaPlusResponse:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        if categoria.activo:
            await self._materia_repo.nullify_categoria(categoria_id)
            categoria.activo = False
        else:
            categoria.activo = True
        await self._session.flush()
        await self._session.refresh(categoria)
        return CategoriaPlusResponse.model_validate(categoria)

    async def listar_materias(self, categoria_id: uuid.UUID) -> dict:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        materias = await self._materia_repo.get_by_categoria(categoria_id)
        return {
            'items': [MateriaResponse.model_validate(m) for m in materias],
            'total': len(materias),
        }

    async def asignacion_masiva(self, categoria_id: uuid.UUID, materia_ids: Sequence[uuid.UUID]) -> dict:
        categoria = await self._repo.get(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail='Categoría no encontrada')
        count = 0
        for materia_id in materia_ids:
            materia = await self._materia_repo.get(materia_id)
            if materia:
                materia.categoria_plus_id = categoria_id
                count += 1
        await self._session.flush()
        return {'count': count, 'total_solicitado': len(materia_ids)}
