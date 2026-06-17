import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    decrypt,
    encrypt,
    hash_dni,
    hash_email,
    hash_password,
)
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate


class UsuarioService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = UsuarioRepository(session, tenant_id)

    async def list_usuarios(
        self, *, estado: str | None = None, skip: int = 0, limit: int = 100,
    ):
        usuarios = await self._repo.list_with_filters(
            estado=estado, skip=skip, limit=limit,
        )
        items = [self._to_response(u) for u in usuarios]
        return {'items': items, 'total': len(items)}

    async def get_usuario(self, usuario_id: uuid.UUID):
        usuario = await self._repo.get(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        return self._to_response(usuario)

    async def create_usuario(self, data: UsuarioCreate):
        email_hash = hash_email(data.email)
        existing = await self._repo.get_by_email_hash(email_hash)
        if existing:
            raise HTTPException(
                status_code=409,
                detail='Ya existe un usuario con ese email en este tenant',
            )

        encrypted_fields = self._encrypt_pii(data)
        usuario = await self._repo.create(
            email=data.email,
            email_cifrado=encrypted_fields['email_cifrado'],
            email_hash=email_hash,
            password_hash=hash_password(data.password),
            nombre_cifrado=encrypted_fields.get('nombre_cifrado'),
            apellido_cifrado=encrypted_fields.get('apellido_cifrado'),
            dni_cifrado=encrypted_fields.get('dni_cifrado'),
            dni_hash=encrypted_fields.get('dni_hash'),
            cuil_cifrado=encrypted_fields.get('cuil_cifrado'),
            cbu_cifrado=encrypted_fields.get('cbu_cifrado'),
            alias_cbu_cifrado=encrypted_fields.get('alias_cbu_cifrado'),
            banco=data.banco,
            regional=data.regional,
            legajo=data.legajo,
            legajo_profesional=data.legajo_profesional,
            facturador=data.facturador,
            estado=data.estado,
        )
        return self._to_response(usuario)

    async def update_usuario(self, usuario_id: uuid.UUID, data: UsuarioUpdate):
        usuario = await self._repo.get(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')

        update_data = {}
        if data.nombre is not None:
            update_data['nombre_cifrado'] = encrypt(data.nombre)
        if data.apellido is not None:
            update_data['apellido_cifrado'] = encrypt(data.apellido)
        if data.dni is not None:
            update_data['dni_cifrado'] = encrypt(data.dni)
            update_data['dni_hash'] = hash_dni(data.dni)
        if data.cuil is not None:
            update_data['cuil_cifrado'] = encrypt(data.cuil)
        if data.cbu is not None:
            update_data['cbu_cifrado'] = encrypt(data.cbu)
        if data.alias_cbu is not None:
            update_data['alias_cbu_cifrado'] = encrypt(data.alias_cbu)
        if data.banco is not None:
            update_data['banco'] = data.banco
        if data.regional is not None:
            update_data['regional'] = data.regional
        if data.legajo is not None:
            update_data['legajo'] = data.legajo
        if data.legajo_profesional is not None:
            update_data['legajo_profesional'] = data.legajo_profesional
        if data.facturador is not None:
            update_data['facturador'] = data.facturador
        if data.estado is not None:
            update_data['estado'] = data.estado
        if data.is_active is not None:
            update_data['is_active'] = data.is_active

        if not update_data:
            return self._to_response(usuario)

        updated = await self._repo.update(usuario, **update_data)
        return self._to_response(updated)

    async def delete_usuario(self, usuario_id: uuid.UUID):
        usuario = await self._repo.get(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        await self._repo.soft_delete(usuario)

    def _encrypt_pii(self, data: UsuarioCreate) -> dict:
        result = {}
        result['email_cifrado'] = encrypt(data.email)
        if data.nombre:
            result['nombre_cifrado'] = encrypt(data.nombre)
        if data.apellido:
            result['apellido_cifrado'] = encrypt(data.apellido)
        if data.dni:
            result['dni_cifrado'] = encrypt(data.dni)
            result['dni_hash'] = hash_dni(data.dni)
        if data.cuil:
            result['cuil_cifrado'] = encrypt(data.cuil)
        if data.cbu:
            result['cbu_cifrado'] = encrypt(data.cbu)
        if data.alias_cbu:
            result['alias_cbu_cifrado'] = encrypt(data.alias_cbu)
        return result

    def _to_response(self, usuario) -> UsuarioResponse:
        nombre = decrypt(usuario.nombre_cifrado) if usuario.nombre_cifrado else None
        apellido = decrypt(usuario.apellido_cifrado) if usuario.apellido_cifrado else None
        email = usuario.email if not usuario.email_cifrado else decrypt(usuario.email_cifrado)
        return UsuarioResponse(
            id=usuario.id,
            tenant_id=usuario.tenant_id,
            email=email,
            nombre=nombre,
            apellido=apellido,
            legajo=usuario.legajo,
            legajo_profesional=usuario.legajo_profesional,
            banco=usuario.banco,
            regional=usuario.regional,
            facturador=usuario.facturador,
            estado=usuario.estado,
            is_active=usuario.is_active,
            roles=usuario.roles or [],
            created_at=usuario.created_at,
            updated_at=usuario.updated_at,
            deleted_at=usuario.deleted_at,
        )