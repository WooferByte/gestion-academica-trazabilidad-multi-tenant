# activia-trace — Instrucciones para levantar el proyecto

## Requisitos

- Python 3.13+
- PostgreSQL 16+
- Node.js 23+
- Docker (opcional)

## 1. Base de datos

### Opción A: Con Docker (recomendado)
```bash
docker compose up -d postgres
```

### Opción B: PostgreSQL local
Crear base de datos llamada `trace`:
```bash
createdb trace
```

## 2. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -e .

# Configurar .env (copiar desde .env.example)
copy .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Ejecutar seed (poblado completo de datos: estructura + finanzas)
python seed.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Frontend

```bash
cd trace-app
npm install
npm run dev
```

## 4. Acceder

Frontend: http://localhost:5173
Backend API: http://localhost:8000/docs

## Credenciales de prueba

| Email | Contraseña | Rol |
|-------|-----------|-----|
| `admin@test.com` | `password123` | ADMIN |
| `ana.profesor@test.com` | `password123` | PROFESOR (Álgebra) |
| `carlos.profesor@test.com` | `password123` | PROFESOR (Programación I) |
| `maria.tutor@test.com` | `password123` | TUTOR |
| `pedro.tutor@test.com` | `password123` | TUTOR |
| `alumno.col1@test.com` | `password123` | ALUMNO |

## Datos precargados

- **3 carreras**: Ingeniería en Sistemas, Lic. Administración, Tecnicatura en Programación
- **6 cohortes**: 2024, 2025, 2026
- **9 materias**: Álgebra, Programación I/II, Base de Datos, Redes, etc.
- **13 usuarios**: 1 admin, 2 profesores, 2 tutores, 1 finanzas, 7 alumnos
- **12 asignaciones** de docentes a materias
- **5 convocatorias a coloquio** con turnos, alumnos convocados, reservas y resultados
- **60 liquidaciones** de ejemplo (Abiertas, Calculadas, Cerradas)
- **9 facturas** (Pendientes y Abonadas)
- **4 salarios base** por rol (PROFESOR, TUTOR, NEXO, COORDINADOR)
- **Avisos**, comunicaciones, tareas, encuentros, guardias, fechas académicas

## Funcionalidades por rol

### ADMIN
- Estructura Académica: CRUD carreras, cohortes, materias
- Usuarios: CRUD usuarios del tenant
- Auditoría: panel de interacciones y log completo
- Liquidaciones: calcular, cerrar, exportar, historial
- Facturas: crear, cambiar estado
- Grilla Salarial: salarios base y categorías plus
- Setup Cuatrimestre: programas, fechas académicas
- Equipos Docentes, Encuentros, Avisos, Tareas, Coloquios

### PROFESOR
- Académico: importar calificaciones, análisis de alumnos atrasados
- Equipos Docentes: mis equipos
- Encuentros: slots, guardias
- Coloquios: reservar turnos, ver resultados
- Comunicaciones: enviar mensajes a alumnos

### FINANZAS
- Liquidaciones, Facturas, Grilla Salarial
