"""Seed script for activia-trace. Call run_seed(session) to populate DB.

All UUIDs are deterministic (uuid5), so tests can reference them via constants.
"""

import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt, hash_email, hash_password
from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.asignacion import Asignacion
from app.models.aviso import Aviso
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.coloquio_alumno import ColoquioAlumno
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.evaluacion import Evaluacion, TipoEvaluacion, EstadoEvaluacion
from app.models.guardia import Guardia, EstadoGuardia
from app.models.instancia_encuentro import InstanciaEncuentro, EstadoInstancia
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.reserva_evaluacion import ReservaEvaluacion, EstadoReserva
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.slot_encuentro import SlotEncuentro, DiaSemana
from app.models.tenant import Tenant
from app.models.turno_coloquio import TurnoColoquio
from app.models.user import User
from app.models.user_role import UserRole
from app.models.version_padron import VersionPadron

NS = uuid.NAMESPACE_DNS

# ── Deterministic UUIDs ──────────────────────────────────────────────────

TENANT_ID = uuid.uuid5(NS, 'seed-tenant-tec')

ROLE_ADMIN_ID = uuid.uuid5(NS, 'seed-role-admin')
ROLE_PROFESOR_ID = uuid.uuid5(NS, 'seed-role-profesor')
ROLE_TUTOR_ID = uuid.uuid5(NS, 'seed-role-tutor')

USER_ADMIN_ID = uuid.uuid5(NS, 'seed-user-admin')
USER_ANA_ID = uuid.uuid5(NS, 'seed-user-ana')
USER_CARLOS_ID = uuid.uuid5(NS, 'seed-user-carlos')
USER_MARIA_ID = uuid.uuid5(NS, 'seed-user-maria')
USER_PEDRO_ID = uuid.uuid5(NS, 'seed-user-pedro')
USER_ALUMNO_COL_1 = uuid.uuid5(NS, 'seed-alumno-col-1')
USER_ALUMNO_COL_2 = uuid.uuid5(NS, 'seed-alumno-col-2')

CARRERA_ING_ID = uuid.uuid5(NS, 'seed-carrera-ing')
CARRERA_ADM_ID = uuid.uuid5(NS, 'seed-carrera-adm')

COHORTE_ING_2024_ID = uuid.uuid5(NS, 'seed-cohorte-ing-2024')
COHORTE_ING_2025_ID = uuid.uuid5(NS, 'seed-cohorte-ing-2025')
COHORTE_ADM_2024_ID = uuid.uuid5(NS, 'seed-cohorte-adm-2024')
COHORTE_ADM_2025_ID = uuid.uuid5(NS, 'seed-cohorte-adm-2025')

MATERIA_ALGEBRA_ID = uuid.uuid5(NS, 'seed-materia-algebra')
MATERIA_PROG1_ID = uuid.uuid5(NS, 'seed-materia-prog1')
MATERIA_PROG2_ID = uuid.uuid5(NS, 'seed-materia-prog2')
MATERIA_BD_ID = uuid.uuid5(NS, 'seed-materia-bd')
MATERIA_REDES_ID = uuid.uuid5(NS, 'seed-materia-redes')
MATERIA_CONTABILIDAD_ID = uuid.uuid5(NS, 'seed-materia-contabilidad')
MATERIA_MARKETING_ID = uuid.uuid5(NS, 'seed-materia-marketing')
MATERIA_RRHH_ID = uuid.uuid5(NS, 'seed-materia-rrhh')

ASIG_ADMIN_ALGEBRA_ID = uuid.uuid5(NS, 'seed-asig-admin-algebra')
ASIG_ANA_ALGEBRA_ID = uuid.uuid5(NS, 'seed-asig-ana-algebra')
ASIG_CARLOS_PROG1_ID = uuid.uuid5(NS, 'seed-asig-carlos-prog1')
ASIG_MARIA_ALGEBRA_ID = uuid.uuid5(NS, 'seed-asig-maria-algebra')
ASIG_PEDRO_PROG1_ID = uuid.uuid5(NS, 'seed-asig-pedro-prog1')
ASIG_PEDRO_BD_ID = uuid.uuid5(NS, 'seed-asig-pedro-bd')

VERSION_ALGEBRA_ID = uuid.uuid5(NS, 'seed-version-algebra')
VERSION_CONTABILIDAD_ID = uuid.uuid5(NS, 'seed-version-contabilidad')

LOTE_COM_ID = uuid.uuid5(NS, 'seed-lote-comunicacion')

AVISO_1_ID = uuid.uuid5(NS, 'seed-aviso-1')
AVISO_2_ID = uuid.uuid5(NS, 'seed-aviso-2')
AVISO_3_ID = uuid.uuid5(NS, 'seed-aviso-3')
AVISO_4_ID = uuid.uuid5(NS, 'seed-aviso-4')
AVISO_5_ID = uuid.uuid5(NS, 'seed-aviso-5')

SLOT_1_ID = uuid.uuid5(NS, 'seed-slot-1')
SLOT_2_ID = uuid.uuid5(NS, 'seed-slot-2')
SLOT_3_ID = uuid.uuid5(NS, 'seed-slot-3')

INSTANCIA_1_ID = uuid.uuid5(NS, 'seed-instancia-1')
INSTANCIA_2_ID = uuid.uuid5(NS, 'seed-instancia-2')
INSTANCIA_3_ID = uuid.uuid5(NS, 'seed-instancia-3')

GUARDIA_1_ID = uuid.uuid5(NS, 'seed-guardia-1')
GUARDIA_2_ID = uuid.uuid5(NS, 'seed-guardia-2')
GUARDIA_3_ID = uuid.uuid5(NS, 'seed-guardia-3')
GUARDIA_4_ID = uuid.uuid5(NS, 'seed-guardia-4')
GUARDIA_5_ID = uuid.uuid5(NS, 'seed-guardia-5')

EVAL_1_ID = uuid.uuid5(NS, 'seed-eval-1')
EVAL_2_ID = uuid.uuid5(NS, 'seed-eval-2')

TURNO_EVAL1_ID = uuid.uuid5(NS, 'seed-turno-eval1-1')
TURNO_EVAL1B_ID = uuid.uuid5(NS, 'seed-turno-eval1-2')
TURNO_EVAL2_ID = uuid.uuid5(NS, 'seed-turno-eval2-1')

# ── Data ─────────────────────────────────────────────────────────────────

ALL_PERMISOS = [
    'estructura:gestionar', 'rbac:gestionar', 'usuarios:gestionar',
    'equipos:asignar', 'padron:cargar', 'calificaciones:importar',
    'atrasados:ver', 'comunicacion:enviar', 'comunicacion:aprobar',
    'avisos:publicar', 'encuentros:gestionar', 'coloquios:gestionar',
    'coloquios:reservar',
]

ALUMNOS = [
    ('Juan', 'Pérez'), ('María', 'García'), ('Carlos', 'López'),
    ('Ana', 'Martínez'), ('Pedro', 'Rodríguez'), ('Laura', 'Fernández'),
    ('Diego', 'González'), ('Sofía', 'Hernández'), ('Miguel', 'Torres'),
    ('Valentina', 'Ramírez'), ('Alejandro', 'Morales'), ('Camila', 'Ortiz'),
    ('Fernando', 'Silva'), ('Isabella', 'Castillo'), ('Santiago', 'Romero'),
    ('Luciana', 'Flores'), ('Mateo', 'Vargas'), ('Emilia', 'Reyes'),
    ('Gabriel', 'Cruz'), ('Victoria', 'Díaz'), ('Nicolás', 'Herrera'),
    ('Julieta', 'Medina'), ('Sebastián', 'Ríos'), ('Antonia', 'Campos'),
    ('Benjamín', 'Peña'), ('Martina', 'Vega'), ('Emiliano', 'Carrasco'),
    ('Valeria', 'Muñoz'), ('Thiago', 'Quinteros'), ('Catalina', 'Navarro'),
]

ACTIVIDADES = ['TP1', 'TP2', 'Parcial', 'Recuperatorio']

# 5 failing students: grades < 60 threshold
FAILING_GRADES = [
    (35, 42, 30, 38),
    (28, 45, 33, 41),
    (40, 35, 50, 38),
    (30, 28, 35, 42),
    (45, 38, 40, 30),
]

PASSING_GRADES = [
    (65, 70, 75, 80),
    (70, 75, 80, 85),
    (75, 80, 85, 90),
    (80, 85, 90, 95),
    (85, 90, 95, 70),
    (90, 85, 80, 75),
    (68, 72, 78, 82),
    (72, 78, 82, 88),
    (78, 82, 88, 92),
    (82, 88, 92, 78),
    (66, 73, 79, 84),
    (74, 79, 84, 89),
    (69, 77, 81, 86),
    (77, 81, 86, 91),
    (71, 76, 83, 87),
    (73, 84, 77, 90),
    (67, 71, 76, 83),
    (79, 83, 89, 93),
    (81, 87, 91, 76),
    (83, 89, 93, 79),
    (68, 74, 80, 86),
    (76, 82, 88, 94),
    (70, 78, 84, 90),
    (84, 90, 76, 82),
    (88, 94, 70, 78),
]

# ── Seed function ────────────────────────────────────────────────────────


async def run_seed(session: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    today = now.date()

    # ── 1. Tenant ────────────────────────────────────────────────────────
    tenant = Tenant(
        id=TENANT_ID, nombre='Universidad Tecnológica Test',
        codigo='TEC', estado='Activo', aprobacion_comunicaciones=False,
    )
    session.add(tenant)
    await session.flush()

    # ── 2. Roles ─────────────────────────────────────────────────────────
    role_admin = Role(id=ROLE_ADMIN_ID, tenant_id=TENANT_ID, name='ADMIN', codigo='ADMIN')
    role_prof = Role(id=ROLE_PROFESOR_ID, tenant_id=TENANT_ID, name='PROFESOR', codigo='PROFESOR')
    role_tutor = Role(id=ROLE_TUTOR_ID, tenant_id=TENANT_ID, name='TUTOR', codigo='TUTOR')
    session.add_all([role_admin, role_prof, role_tutor])
    await session.flush()

    # ── Permissions & RolePermissions ────────────────────────────────────
    for codigo in ALL_PERMISOS:
        modulo, accion = codigo.split(':')
        perm_id = uuid.uuid5(NS, f'seed-perm-{codigo.replace(":", "-")}')
        session.add(Permission(
            id=perm_id, tenant_id=TENANT_ID,
            codigo=codigo, modulo=modulo, accion=accion,
        ))
    await session.flush()
    for codigo in ALL_PERMISOS:
        perm_id = uuid.uuid5(NS, f'seed-perm-{codigo.replace(":", "-")}')
        for role_id in [ROLE_ADMIN_ID, ROLE_PROFESOR_ID, ROLE_TUTOR_ID]:
            rp_id = uuid.uuid5(NS, f'seed-rp-{role_id}-{codigo.replace(":", "-")}')
            session.add(RolePermission(
                id=rp_id, tenant_id=TENANT_ID,
                role_id=role_id, permiso_id=perm_id,
                propio=True,
            ))

    # ── 3. Users ─────────────────────────────────────────────────────────
    users_data = [
        (USER_ADMIN_ID, 'admin@test.com', 'admin'),
        (USER_ANA_ID, 'ana.profesor@test.com', 'profesor'),
        (USER_CARLOS_ID, 'carlos.profesor@test.com', 'profesor'),
        (USER_MARIA_ID, 'maria.tutor@test.com', 'tutor'),
        (USER_PEDRO_ID, 'pedro.tutor@test.com', 'tutor'),
        (USER_ALUMNO_COL_1, 'alumno.col1@test.com', 'alumno'),
        (USER_ALUMNO_COL_2, 'alumno.col2@test.com', 'alumno'),
    ]
    role_map = {'admin': ROLE_ADMIN_ID, 'profesor': ROLE_PROFESOR_ID, 'tutor': ROLE_TUTOR_ID, 'alumno': ROLE_ADMIN_ID}
    for uid, email, rol in users_data:
        role_upper = rol.upper() if rol != 'alumno' else 'alumno'
        user = User(
            id=uid, tenant_id=TENANT_ID, email=email,
            email_cifrado=encrypt(email), email_hash=hash_email(email),
            password_hash=hash_password('password123'),
            roles=[role_upper], estado='Activo', is_active=True,
        )
        session.add(user)
        role_id = role_map[rol]
        ur_id = uuid.uuid5(NS, f'seed-ur-{uid}')
        session.add(UserRole(id=ur_id, tenant_id=TENANT_ID, user_id=uid, role_id=role_id))
    await session.flush()  # ensure users exist before asignaciones

    # ── 4. Carreras ──────────────────────────────────────────────────────
    session.add(Carrera(id=CARRERA_ING_ID, tenant_id=TENANT_ID, codigo='ING-2020', nombre='Ingeniería en Sistemas', estado='Activa'))
    session.add(Carrera(id=CARRERA_ADM_ID, tenant_id=TENANT_ID, codigo='LIC-ADM-2020', nombre='Lic. Administración', estado='Activa'))
    await session.flush()

    # ── 5. Cohortes ──────────────────────────────────────────────────────
    cohortes_data = [
        (COHORTE_ING_2024_ID, CARRERA_ING_ID, '2024', 2024),
        (COHORTE_ING_2025_ID, CARRERA_ING_ID, '2025', 2025),
        (COHORTE_ADM_2024_ID, CARRERA_ADM_ID, '2024', 2024),
        (COHORTE_ADM_2025_ID, CARRERA_ADM_ID, '2025', 2025),
    ]
    for cid, carrera_id, nombre, anio in cohortes_data:
        session.add(Cohorte(
            id=cid, tenant_id=TENANT_ID, carrera_id=carrera_id,
            nombre=nombre, anio=anio,
            vig_desde=date(anio, 1, 1), estado='Activa',
        ))
    await session.flush()

    # ── 6. Materias ──────────────────────────────────────────────────────
    session.add_all([
        Materia(id=MATERIA_ALGEBRA_ID, tenant_id=TENANT_ID, codigo='ALG101', nombre='Álgebra', estado='Activa'),
        Materia(id=MATERIA_PROG1_ID, tenant_id=TENANT_ID, codigo='PRG101', nombre='Programación I', estado='Activa'),
        Materia(id=MATERIA_PROG2_ID, tenant_id=TENANT_ID, codigo='PRG201', nombre='Programación II', estado='Activa'),
        Materia(id=MATERIA_BD_ID, tenant_id=TENANT_ID, codigo='BD101', nombre='Base de Datos', estado='Activa'),
        Materia(id=MATERIA_REDES_ID, tenant_id=TENANT_ID, codigo='RED101', nombre='Redes', estado='Activa'),
        Materia(id=MATERIA_CONTABILIDAD_ID, tenant_id=TENANT_ID, codigo='CON101', nombre='Contabilidad I', estado='Activa'),
        Materia(id=MATERIA_MARKETING_ID, tenant_id=TENANT_ID, codigo='MKT101', nombre='Marketing', estado='Activa'),
        Materia(id=MATERIA_RRHH_ID, tenant_id=TENANT_ID, codigo='RRHH101', nombre='Gestión de RRHH', estado='Activa'),
    ])
    await session.flush()

    # ── 7. Asignaciones ──────────────────────────────────────────────────
    session.add_all([
        Asignacion(id=ASIG_ADMIN_ALGEBRA_ID, tenant_id=TENANT_ID, usuario_id=USER_ADMIN_ID,
                   rol='PROFESOR', materia_id=MATERIA_ALGEBRA_ID, cohorte_id=COHORTE_ING_2024_ID),
        Asignacion(id=ASIG_ANA_ALGEBRA_ID, tenant_id=TENANT_ID, usuario_id=USER_ANA_ID,
                   rol='PROFESOR', materia_id=MATERIA_ALGEBRA_ID, cohorte_id=COHORTE_ING_2024_ID),
        Asignacion(id=ASIG_CARLOS_PROG1_ID, tenant_id=TENANT_ID, usuario_id=USER_CARLOS_ID,
                   rol='PROFESOR', materia_id=MATERIA_PROG1_ID, cohorte_id=COHORTE_ING_2024_ID),
        Asignacion(id=ASIG_MARIA_ALGEBRA_ID, tenant_id=TENANT_ID, usuario_id=USER_MARIA_ID,
                   rol='TUTOR', materia_id=MATERIA_ALGEBRA_ID, cohorte_id=COHORTE_ING_2024_ID),
        Asignacion(id=ASIG_PEDRO_PROG1_ID, tenant_id=TENANT_ID, usuario_id=USER_PEDRO_ID,
                   rol='TUTOR', materia_id=MATERIA_PROG1_ID, cohorte_id=COHORTE_ING_2024_ID),
        Asignacion(id=ASIG_PEDRO_BD_ID, tenant_id=TENANT_ID, usuario_id=USER_PEDRO_ID,
                   rol='TUTOR', materia_id=MATERIA_BD_ID, cohorte_id=COHORTE_ING_2025_ID),
    ])
    await session.flush()

    # ── 8. Padron ────────────────────────────────────────────────────────
    # Version + Entradas for Algebra / ING-2024
    session.add(VersionPadron(
        id=VERSION_ALGEBRA_ID, tenant_id=TENANT_ID,
        materia_id=MATERIA_ALGEBRA_ID, cohorte_id=COHORTE_ING_2024_ID,
        cargado_por=USER_ADMIN_ID, activa=True,
    ))
    # Version + Entradas for Contabilidad / ADM-2024
    session.add(VersionPadron(
        id=VERSION_CONTABILIDAD_ID, tenant_id=TENANT_ID,
        materia_id=MATERIA_CONTABILIDAD_ID, cohorte_id=COHORTE_ADM_2024_ID,
        cargado_por=USER_ADMIN_ID, activa=True,
    ))
    await session.flush()  # ensure version_padron exists before entrada_padron

    entrada_ids_algebra = []
    entrada_ids_contabilidad = []
    for i, (nombre, apellido) in enumerate(ALUMNOS):
        email = f'{nombre.lower()}.{apellido.lower()}@test.com'
        comision = 'A' if i < 15 else 'B'
        regional = 'CABA' if i < 10 else ('GBA' if i < 20 else 'Interior')

        eid_a = uuid.uuid5(NS, f'seed-entrada-algebra-{i}')
        session.add(EntradaPadron(
            id=eid_a, tenant_id=TENANT_ID, version_id=VERSION_ALGEBRA_ID,
            nombre=nombre, apellidos=apellido, email=email,
            comision=comision, regional=regional,
        ))
        entrada_ids_algebra.append(eid_a)

        eid_c = uuid.uuid5(NS, f'seed-entrada-contabilidad-{i}')
        session.add(EntradaPadron(
            id=eid_c, tenant_id=TENANT_ID, version_id=VERSION_CONTABILIDAD_ID,
            nombre=nombre, apellidos=apellido, email=email,
            comision=comision, regional=regional,
        ))
        entrada_ids_contabilidad.append(eid_c)
    await session.flush()  # ensure entrada_padron exists before calificaciones

    # ── 9. Calificaciones (240+) ─────────────────────────────────────────
    # Algebra: 30 alumnos × 4 actividades = 120
    _create_calificaciones(session, MATERIA_ALGEBRA_ID, COHORTE_ING_2024_ID, entrada_ids_algebra, FAILING_GRADES, PASSING_GRADES)
    # Contabilidad: 30 alumnos × 4 actividades = 120
    _create_calificaciones(session, MATERIA_CONTABILIDAD_ID, COHORTE_ADM_2024_ID, entrada_ids_contabilidad, FAILING_GRADES, PASSING_GRADES)

    # ── 10. Comunicaciones (5+) ──────────────────────────────────────────
    coms = [
        (uuid.uuid5(NS, 'seed-com-1'), 'admin@test.com', 'Bienvenido al sistema',
         'Este es un mensaje de bienvenida para el alumno.', EstadoComunicacion.ENVIADO, False, None),
        (uuid.uuid5(NS, 'seed-com-2'), 'alumno1@test.com', 'Recordatorio de parcial',
         'El examen parcial se acerca. Estudien.', EstadoComunicacion.PENDIENTE, False, None),
        (uuid.uuid5(NS, 'seed-com-3'), 'alumno2@test.com', 'Aviso de nota',
         'Su calificación ha sido publicada.', EstadoComunicacion.ENVIADO, False, None),
        (uuid.uuid5(NS, 'seed-com-4'), 'alumno3@test.com', 'Suspensión de clases',
         'Las clases del viernes se suspenden.', EstadoComunicacion.CANCELADO, True, None),
        (uuid.uuid5(NS, 'seed-com-5'), 'alumno4@test.com', 'Invitación a coloquio',
         'Ha sido convocado al coloquio final.', EstadoComunicacion.PENDIENTE, False,
         now + timedelta(days=7)),
        (uuid.uuid5(NS, 'seed-com-6'), 'alumno5@test.com', 'Programada futura',
         'Esta comunicación está programada.', EstadoComunicacion.PENDIENTE, False,
         now + timedelta(days=30)),
    ]
    for cid, dest, asunto, cuerpo, estado, aprob_req, prog_para in coms:
        session.add(Comunicacion(
            id=cid, tenant_id=TENANT_ID, enviado_por=USER_ADMIN_ID,
            materia_id=MATERIA_ALGEBRA_ID,
            destinatario=encrypt(dest), asunto=asunto, cuerpo=cuerpo,
            estado=estado, lote_id=LOTE_COM_ID,
            aprobacion_requerida=aprob_req,
            programada_para=prog_para,
        ))

    # ── 11. Avisos (5+) ──────────────────────────────────────────────────
    avisos_activos = [
        (AVISO_1_ID, 'Global', 'Info', 'Inicio de clases',
         'Bienvenidos al nuevo cuatrimestre.', now - timedelta(days=1), now + timedelta(days=30)),
        (AVISO_2_ID, 'Global', 'Advertencia', 'Mantenimiento programado',
         'El sistema estará fuera de línea el sábado.', now - timedelta(days=1), now + timedelta(days=15)),
        (AVISO_3_ID, 'PorMateria', 'Crítico', 'Cambio de aula',
         'Álgebra cambió al aula 301.', now - timedelta(days=1), now + timedelta(days=7)),
    ]
    avisos_expirados = [
        (AVISO_4_ID, 'Global', 'Info', 'Feriado nacional',
         'No habrá clases el 25 de mayo.', now - timedelta(days=60), now - timedelta(days=30)),
        (AVISO_5_ID, 'PorMateria', 'Advertencia', 'Inscripción cerrada',
         'La inscripción a Programación I cerró.', now - timedelta(days=45), now - timedelta(days=15)),
    ]
    for aid, alcance, severidad, titulo, cuerpo, inicio, fin in avisos_activos + avisos_expirados:
        kwargs = dict(
            id=aid, tenant_id=TENANT_ID, alcance=alcance, severidad=severidad,
            titulo=titulo, cuerpo=cuerpo, inicio_vigencia=inicio, fin_vigencia=fin,
            orden=1, activo=True, requiere_ack=False,
        )
        if alcance == 'PorMateria':
            kwargs['materia_id'] = MATERIA_ALGEBRA_ID
        session.add(Aviso(**kwargs))

    # ── 12. Encuentros (3 slots + 3 instancias) ──────────────────────────
    session.add_all([
        SlotEncuentro(id=SLOT_1_ID, tenant_id=TENANT_ID, asignacion_id=ASIG_ADMIN_ALGEBRA_ID,
                      materia_id=MATERIA_ALGEBRA_ID, titulo='Álgebra Lunes',
                      hora='18:00', dia_semana=DiaSemana.LUNES,
                      fecha_inicio=today, cant_semanas=16),
        SlotEncuentro(id=SLOT_2_ID, tenant_id=TENANT_ID, asignacion_id=ASIG_ANA_ALGEBRA_ID,
                      materia_id=MATERIA_ALGEBRA_ID, titulo='Álgebra Miércoles',
                      hora='18:00', dia_semana=DiaSemana.MIERCOLES,
                      fecha_inicio=today, cant_semanas=16),
        SlotEncuentro(id=SLOT_3_ID, tenant_id=TENANT_ID, asignacion_id=ASIG_ADMIN_ALGEBRA_ID,
                      materia_id=MATERIA_ALGEBRA_ID, titulo='Consultas Viernes',
                      hora='16:00', dia_semana=DiaSemana.VIERNES,
                      fecha_inicio=today, cant_semanas=16),
    ])
    await session.flush()
    session.add_all([
        InstanciaEncuentro(id=INSTANCIA_1_ID, tenant_id=TENANT_ID, slot_id=SLOT_1_ID,
                           materia_id=MATERIA_ALGEBRA_ID,
                           fecha=today, hora='18:00', titulo='Clase 1'),
        InstanciaEncuentro(id=INSTANCIA_2_ID, tenant_id=TENANT_ID, slot_id=SLOT_2_ID,
                           materia_id=MATERIA_ALGEBRA_ID,
                           fecha=today + timedelta(days=2), hora='18:00', titulo='Clase 2'),
        InstanciaEncuentro(id=INSTANCIA_3_ID, tenant_id=TENANT_ID, slot_id=SLOT_3_ID,
                           materia_id=MATERIA_ALGEBRA_ID,
                           fecha=today + timedelta(days=4), hora='16:00', titulo='Consulta 1'),
    ])

    # ── 13. Guardias (5+) ────────────────────────────────────────────────
    guardias_data = [
        (GUARDIA_1_ID, ASIG_MARIA_ALGEBRA_ID, MATERIA_ALGEBRA_ID, CARRERA_ING_ID, COHORTE_ING_2024_ID,
         DiaSemana.LUNES, '18:00-19:00', EstadoGuardia.PENDIENTE),
        (GUARDIA_2_ID, ASIG_MARIA_ALGEBRA_ID, MATERIA_ALGEBRA_ID, CARRERA_ING_ID, COHORTE_ING_2024_ID,
         DiaSemana.MIERCOLES, '18:00-19:00', EstadoGuardia.PENDIENTE),
        (GUARDIA_3_ID, ASIG_PEDRO_PROG1_ID, MATERIA_PROG1_ID, CARRERA_ING_ID, COHORTE_ING_2024_ID,
         DiaSemana.MARTES, '16:00-17:00', EstadoGuardia.REALIZADA),
        (GUARDIA_4_ID, ASIG_PEDRO_BD_ID, MATERIA_BD_ID, CARRERA_ING_ID, COHORTE_ING_2025_ID,
         DiaSemana.JUEVES, '14:00-15:00', EstadoGuardia.PENDIENTE),
        (GUARDIA_5_ID, ASIG_ADMIN_ALGEBRA_ID, MATERIA_ALGEBRA_ID, CARRERA_ING_ID, COHORTE_ING_2024_ID,
         DiaSemana.VIERNES, '10:00-11:30', EstadoGuardia.PENDIENTE),
    ]
    for gid, asig_id, mat_id, car_id, coh_id, dia, horario, estado in guardias_data:
        session.add(Guardia(
            id=gid, tenant_id=TENANT_ID, asignacion_id=asig_id,
            materia_id=mat_id, carrera_id=car_id, cohorte_id=coh_id,
            dia=dia, horario=horario, estado=estado,
        ))

    # ── 14. Coloquios (2 convocatorias) ──────────────────────────────────
    session.add_all([
        Evaluacion(id=EVAL_1_ID, tenant_id=TENANT_ID,
                   materia_id=MATERIA_ALGEBRA_ID, cohorte_id=COHORTE_ING_2024_ID,
                   tipo=TipoEvaluacion.PARCIAL, instancia='Primer Parcial',
                   estado=EstadoEvaluacion.ACTIVA, dias_disponibles=5),
        Evaluacion(id=EVAL_2_ID, tenant_id=TENANT_ID,
                   materia_id=MATERIA_CONTABILIDAD_ID, cohorte_id=COHORTE_ADM_2024_ID,
                   tipo=TipoEvaluacion.COLOQUIO, instancia='Coloquio Final',
                   estado=EstadoEvaluacion.ACTIVA, dias_disponibles=3),
    ])
    await session.flush()

    session.add_all([
        TurnoColoquio(id=TURNO_EVAL1_ID, tenant_id=TENANT_ID, evaluacion_id=EVAL_1_ID,
                      fecha=date(today.year, today.month, today.day) + timedelta(days=7),
                      hora_inicio=time(9, 0), hora_fin=time(11, 0), cupo=30),
        TurnoColoquio(id=TURNO_EVAL1B_ID, tenant_id=TENANT_ID, evaluacion_id=EVAL_1_ID,
                      fecha=date(today.year, today.month, today.day) + timedelta(days=8),
                      hora_inicio=time(14, 0), hora_fin=time(16, 0), cupo=25),
        TurnoColoquio(id=TURNO_EVAL2_ID, tenant_id=TENANT_ID, evaluacion_id=EVAL_2_ID,
                      fecha=date(today.year, today.month, today.day) + timedelta(days=14),
                      hora_inicio=time(10, 0), hora_fin=time(12, 0), cupo=20),
    ])
    await session.flush()

    # Alumnos for coloquios
    session.add_all([
        ColoquioAlumno(id=uuid.uuid5(NS, 'seed-col-alumno-1'), tenant_id=TENANT_ID,
                       evaluacion_id=EVAL_1_ID, alumno_id=USER_ALUMNO_COL_1),
        ColoquioAlumno(id=uuid.uuid5(NS, 'seed-col-alumno-2'), tenant_id=TENANT_ID,
                       evaluacion_id=EVAL_1_ID, alumno_id=USER_ALUMNO_COL_2),
        ColoquioAlumno(id=uuid.uuid5(NS, 'seed-col-alumno-3'), tenant_id=TENANT_ID,
                       evaluacion_id=EVAL_2_ID, alumno_id=USER_ALUMNO_COL_1),
    ])

    # Reservas
    session.add_all([
        ReservaEvaluacion(id=uuid.uuid5(NS, 'seed-reserva-1'), tenant_id=TENANT_ID,
                          turno_id=TURNO_EVAL1_ID, alumno_id=USER_ALUMNO_COL_1,
                          evaluacion_id=EVAL_1_ID, estado=EstadoReserva.ACTIVA),
        ReservaEvaluacion(id=uuid.uuid5(NS, 'seed-reserva-2'), tenant_id=TENANT_ID,
                          turno_id=TURNO_EVAL1_ID, alumno_id=USER_ALUMNO_COL_2,
                          evaluacion_id=EVAL_1_ID, estado=EstadoReserva.ACTIVA),
    ])

    # Resultados
    session.add_all([
        ResultadoEvaluacion(id=uuid.uuid5(NS, 'seed-resultado-1'), tenant_id=TENANT_ID,
                            evaluacion_id=EVAL_1_ID, alumno_id=USER_ALUMNO_COL_1,
                            nota_final='Aprobado'),
        ResultadoEvaluacion(id=uuid.uuid5(NS, 'seed-resultado-2'), tenant_id=TENANT_ID,
                            evaluacion_id=EVAL_1_ID, alumno_id=USER_ALUMNO_COL_2,
                            nota_final='Satisfactorio'),
    ])

    await session.flush()


def _create_calificaciones(
    session: AsyncSession,
    materia_id: uuid.UUID,
    cohorte_id: uuid.UUID,
    entrada_ids: list[uuid.UUID],
    failing_grades: list[tuple[float, float, float, float]],
    passing_grades: list[tuple[float, float, float, float]],
) -> None:
    for i, ep_id in enumerate(entrada_ids):
        is_failing = i < len(failing_grades)
        grades = failing_grades[i] if is_failing else passing_grades[(i - len(failing_grades)) % len(passing_grades)]
        for j, actividad in enumerate(ACTIVIDADES):
            calif_id = uuid.uuid5(NS, f'seed-calif-{materia_id}-{i}-{j}')
            session.add(Calificacion(
                id=calif_id, tenant_id=TENANT_ID,
                entrada_padron_id=ep_id,
                materia_id=materia_id, cohorte_id=cohorte_id,
                actividad=actividad, nota_numerica=grades[j],
                origen='Importado',
            ))
