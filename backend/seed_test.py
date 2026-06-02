"""
Seed script para testing manual de C-03 auth-jwt-2fa.

Crea:
- 1 tenant de prueba (TEST)
- 1 usuario admin con contraseña conocida
- 1 usuario con 2FA habilitado

Uso: python seed_test.py
Requiere: DB postgres corriendo y .env configurado
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.core.security import encrypt, hash_password
from app.models.tenant import Tenant
from app.models.user import User

settings = Settings()
engine = create_async_engine(str(settings.database_url))
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def seed():
    async with SessionLocal() as session:
        # --- TENANT ---
        tenant_id = uuid.uuid4()
        tenant = Tenant(
            id=tenant_id,
            nombre="Tenant de Prueba",
            codigo="TEST",
            estado="Activo",
        )
        session.add(tenant)

        # --- USUARIO SIN 2FA ---
        user1 = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            nombre_cifrado=encrypt("Admin"),
            apellido_cifrado=encrypt("Test"),
            roles=["admin", "profesor"],
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(user1)

        # --- USUARIO CON 2FA (secreto TOTP pre-generado) ---
        import pyotp
        totp_secret = pyotp.random_base32()
        user2 = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="docente@test.com",
            password_hash=hash_password("docente456"),
            nombre_cifrado=encrypt("Docente"),
            apellido_cifrado=encrypt("Prueba"),
            roles=["profesor"],
            totp_secret_cifrado=encrypt(totp_secret),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(user2)

        await session.commit()

        print("✅ Seed completado exitosamente")
        print(f"  Tenant ID:  {tenant_id}")
        print(f"  Sin 2FA:    admin@test.com / admin123")
        print(f"  Con 2FA:    docente@test.com / docente456")
        print(f"  TOTP Secret para 2FA: {totp_secret}")


if __name__ == "__main__":
    asyncio.run(seed())
