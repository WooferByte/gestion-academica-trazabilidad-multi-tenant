import uuid
from datetime import datetime, timezone

import pytest_asyncio
from sqlalchemy import select

from app.core.security import create_access_token, encrypt, hash_email, hash_password
from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.models.version_padron import VersionPadron


@pytest_asyncio.fixture
async def admin_tenant(db_session):
    tid = uuid.uuid4()
    t = Tenant(id=tid, nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def admin_setup(db_session, admin_tenant):
    tid = admin_tenant.id
    email = 'admin@test.com'
    user = User(
        tenant_id=tid,
        email=email,
        email_cifrado=encrypt(email),
        email_hash=hash_email(email),
        password_hash=hash_password('admin123'),
        roles=['ADMIN'],
    )
    db_session.add(user)

    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add(role_admin)

    p_analisis = Permission(
        tenant_id=tid, codigo='atrasados:ver', modulo='analisis', accion='ver',
    )
    db_session.add(p_analisis)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_analisis.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'user': user}


@pytest_asyncio.fixture
async def tenant2(db_session):
    tid = uuid.uuid4()
    t = Tenant(id=tid, nombre='Tenant2', codigo='TN2', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def base_entities(db_session, admin_tenant):
    carrera = Carrera(tenant_id=admin_tenant.id, codigo='ING', nombre='Ingenieria')
    db_session.add(carrera)
    await db_session.flush()

    materia = Materia(tenant_id=admin_tenant.id, codigo='MATE', nombre='Matematicas')
    db_session.add(materia)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=admin_tenant.id, carrera_id=carrera.id,
        nombre='2026', anio=2026,
        vig_desde=datetime.now(timezone.utc).date(),
    )
    db_session.add(cohorte)
    await db_session.flush()

    return {'materia': materia, 'cohorte': cohorte, 'carrera': carrera}


@pytest_asyncio.fixture
async def padron_setup(db_session, admin_tenant, admin_setup, base_entities):
    version = VersionPadron(
        tenant_id=admin_tenant.id,
        materia_id=base_entities['materia'].id,
        cohorte_id=base_entities['cohorte'].id,
        cargado_por=admin_setup['user'].id,
        activa=True,
    )
    db_session.add(version)
    await db_session.flush()

    entradas = [
        EntradaPadron(
            tenant_id=admin_tenant.id, version_id=version.id,
            nombre=n, apellidos=a, email=e,
            comision='A', regional='CABA',
        )
        for n, a, e in [
            ('Juan', 'Perez', 'juan@test.com'),
            ('Maria', 'Garcia', 'maria@test.com'),
            ('Carlos', 'Lopez', 'carlos@test.com'),
        ]
    ]
    db_session.add_all(entradas)
    await db_session.flush()
    return {'version': version, 'entradas': entradas}


@pytest_asyncio.fixture
async def calificaciones_setup(db_session, admin_tenant, base_entities, padron_setup):
    entradas = padron_setup['entradas']
    califs = [
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[0].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP1', nota_numerica=85.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[0].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP2', nota_numerica=70.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[0].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='Parcial', nota_numerica=90.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[1].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP1', nota_numerica=55.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[1].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP2', nota_numerica=None, nota_textual='No satisfactorio',
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[2].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP1', nota_numerica=75.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[2].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='TP2', nota_numerica=80.0, nota_textual=None,
            origen='Importado',
        ),
        Calificacion(
            tenant_id=admin_tenant.id,
            entrada_padron_id=entradas[2].id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividad='Parcial', nota_numerica=65.0, nota_textual=None,
            origen='Importado',
        ),
    ]
    db_session.add_all(califs)
    await db_session.flush()
    return califs


@pytest_asyncio.fixture
async def tutor_setup(db_session, admin_tenant, admin_setup, base_entities):
    email = 'tutor@test.com'
    user = User(
        tenant_id=admin_tenant.id,
        email=email,
        email_cifrado=encrypt(email),
        email_hash=hash_email(email),
        password_hash=hash_password('tutor123'),
        roles=['TUTOR'],
    )
    db_session.add(user)

    role_tutor = Role(tenant_id=admin_tenant.id, name='TUTOR', codigo='TUTOR')
    db_session.add(role_tutor)
    await db_session.flush()

    from sqlalchemy import select
    result = await db_session.execute(
        select(Permission).where(Permission.tenant_id == admin_tenant.id).where(Permission.codigo == 'atrasados:ver'),
    )
    p_analisis = result.scalar_one_or_none()

    db_session.add_all([
        RolePermission(tenant_id=admin_tenant.id, role_id=role_tutor.id, permiso_id=p_analisis.id),
        UserRole(tenant_id=admin_tenant.id, user_id=user.id, role_id=role_tutor.id),
    ])

    asignacion = Asignacion(
        tenant_id=admin_tenant.id,
        usuario_id=user.id,
        rol='TUTOR',
        materia_id=base_entities['materia'].id,
        cohorte_id=base_entities['cohorte'].id,
    )
    db_session.add(asignacion)
    await db_session.flush()

    token = create_access_token(str(user.id), str(admin_tenant.id), ['TUTOR'])
    return {'token': token, 'user': user, 'asignacion': asignacion}
