import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt, encrypt
from app.repositories.usuario import UsuarioRepository
from app.schemas.perfil import PerfilResponse, PerfilUpdate


class PerfilService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = UsuarioRepository(session, tenant_id)

    async def get_profile(self, user_id: uuid.UUID) -> PerfilResponse:
        user = await self._repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        return self._to_response(user)

    async def update_profile(self, user_id: uuid.UUID, data: PerfilUpdate) -> PerfilResponse:
        user = await self._repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')

        update_data = {}
        if data.nombre is not None:
            update_data['nombre_cifrado'] = encrypt(data.nombre)
        if data.apellido is not None:
            update_data['apellido_cifrado'] = encrypt(data.apellido)
        if data.cbu is not None:
            update_data['cbu_cifrado'] = encrypt(data.cbu)
        if data.alias_cbu is not None:
            update_data['alias_cbu_cifrado'] = encrypt(data.alias_cbu)
        if data.banco is not None:
            update_data['banco'] = data.banco
        if data.regional is not None:
            update_data['regional'] = data.regional
        if data.facturador is not None:
            update_data['facturador'] = data.facturador

        if not update_data:
            return self._to_response(user)

        updated = await self._repo.update(user, **update_data)
        return self._to_response(updated)

    def _to_response(self, user) -> PerfilResponse:
        nombre = decrypt(user.nombre_cifrado) if user.nombre_cifrado else None
        apellido = decrypt(user.apellido_cifrado) if user.apellido_cifrado else None
        dni = decrypt(user.dni_cifrado) if user.dni_cifrado else None
        cuil = decrypt(user.cuil_cifrado) if user.cuil_cifrado else None
        cbu = decrypt(user.cbu_cifrado) if user.cbu_cifrado else None
        alias_cbu = decrypt(user.alias_cbu_cifrado) if user.alias_cbu_cifrado else None

        return PerfilResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            cuil=cuil,
            cbu=cbu,
            alias_cbu=alias_cbu,
            banco=user.banco,
            regional=user.regional,
            legajo=user.legajo,
            legajo_profesional=user.legajo_profesional,
            facturador=user.facturador,
            estado=user.estado,
            roles=user.roles or [],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
