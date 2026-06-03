## Context

activia-trace tiene 14 tablas en DB tras C-01 a C-08. El modelo de datos incluye Tenant, Usuario, Asignación, Materia, Cohorte, Carrera con multi-tenancy row-level, soft delete, y Clean Architecture por capas. C-09 agrega el padrón versionado de alumnos por materia×cohorte con integración Moodle WS (skeleton) y carga manual.

El flujo de importación de padrón es prerrequisito para calificaciones (C-10), atrasados (C-11) y comunicaciones (C-12).

## Goals / Non-Goals

**Goals:**
- Modelos `VersionPadron` + `EntradaPadron` versionados (snapshot completo — ADR-005)
- Import manual xlsx/csv con vista previa + confirmación
- Cliente Moodle WS skeleton que simula sync y mapea errores a 502
- Vaciar datos de padrón de una materia (soft delete, scope RN-04)
- Audit `PADRON_CARGAR` para import y vaciado
- Migración Alembic 007
- Tests de versionado, import, entrada sin usuario_id, aislamiento tenant, mock Moodle WS + 502

**Non-Goals:**
- Importación de calificaciones (C-10)
- Sync nocturna real de Moodle WS (solo estructura)
- Interfaz frontend (C-22)
- Integración real contra Moodle (solo skeleton mockeable)

## Decisions

| Decisión | Opción | Alternativa considerada | Razón |
|----------|--------|------------------------|-------|
| **Versionado** | Snapshot completo (ADR-005) | Deltas | Simplicidad: cada versión contiene el padrón completo. Activar una nueva desactiva la anterior. Coincide con RN-05 (upsert destructivo a nivel versión). |
| **Import preview** | En memoria con Pydantic | Tabla temporal | No persiste hasta confirmación del usuario. Más simple y sin contaminar DB. |
| **usuario_id nullable** | Sí, nullable en `EntradaPadron` | No permitir nulo | Un alumno puede no tener cuenta aún. Se relaciona después cuando se crea su usuario. |
| **Moodle WS skeleton** | Clase mock con retorno fijo + error 502 | Cliente HTTP real | C-09 no tiene conexión Moodle real configurada. El skeleton define el contrato (métodos, tipos, errores) para integrar después. |
| **openpyxl** | Dependencia explícita | pandas | pandas es overkill para leer columnas simples de un xlsx. openpyxl es liviano y suficiente. |
| **Vaciar materia** | Soft delete de entradas + desactivar versión | Hard delete | Consistente con regla de soft delete del proyecto. Audit obligatorio. |

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Archivos xlsx grandes (>10MB) pueden saturar memoria | Limitar tamaño por configuración; rechazar archivos > umbral con 413 |
| Vista previa en memoria se pierde si el usuario no confirma | Diseño intencional: no persiste hasta confirmación explícita |
| EntradaPadron sin usuario_id queda huérfana | Feature, no bug: se vincula cuando el alumno crea cuenta (cambio futuro) |
| Migración 007 conflictúa con cambios paralelos en C-08 | C-08 y C-09 están en GATE 6 con agentes distintos. Asegurar que migrations no compartan el mismo revision_id. |

## Migration Plan

1. Agregar `openpyxl` a `pyproject.toml`
2. Generar migración Alembic 007 con `alembic revision --autogenerate -m "create_version_padron_tables"`
3. Revisar y ajustar manualmente la migración (unique constraint, índices)
4. Ejecutar `alembic upgrade head`

Rollback: `alembic downgrade -1` (drop tablas `entrada_padron`, `version_padron`)

## Open Questions

- ¿El preview debe incluir detección de duplicados por email dentro del mismo archivo? → Se resuelve en implementación, validar en service.
- ¿Formato exacto de columnas esperadas en xlsx/csv? → Definir convención: `nombre`, `apellidos`, `email`, `comision`, `regional`.
