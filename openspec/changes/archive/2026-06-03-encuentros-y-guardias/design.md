## Context

activia-trace tiene ~19 tablas con multi-tenancy row-level, Clean Architecture (Routers → Services → Repositories → Models), SQLAlchemy async, FastAPI. Los módulos de calificaciones, análisis, equipo docente y comunicaciones están operativos. No existe aún modelo de encuentros ni guardias. Se incorporan tres nuevas entidades (E9, E10, E11 del modelo de datos) que se integran con las tablas existentes de `asignacion`, `usuario` y `materia`.

## Goals / Non-Goals

**Goals:**
- Modelos SQLAlchemy para `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con tenant isolation
- Endpoints REST para CRUD de slots recurrentes y encuentros únicos
- Generación automática de N instancias al crear un slot según `cant_semanas` (RN-13)
- Edición de instancias: estado (Programado/Realizado/Cancelado), meet_url, video_url, comentario
- Generación de bloque HTML formateado para el aula virtual
- Vista global de encuentros del tenant para COORDINADOR/ADMIN
- Registro de guardias con consulta filtrada + export CSV
- Permiso `encuentros:gestionar` en guard de endpoints
- Migración Alembic 010
- Tests con DB real

**Non-Goals:**
- Notificaciones push/email sobre encuentros (fuera de scope)
- Calendario ICS o integración con Google Calendar
- Eliminación de slots (solo soft delete)
- Gestión de asistencia a encuentros
- Workflow de aprobación de guardias

## Decisions

| Decisión | Opción elegida | Alternativa | Razón |
|----------|---------------|-------------|-------|
| Generación de instancias | Server-side al crear slot | Bajo demanda con cálculo dinámico | Las instancias son editables individualmente (F6.3); necesitan filas propias en DB |
| Slot vs Instancia | Dos tablas separadas | Una sola tabla con nullable recurrencia | Clean separation: Slot = plantilla, Instancia = ocurrencia concreta. Coincide con E9/E10 del modelo |
| Guardia como entidad propia | Tabla independiente con estado | Embed en SlotEncuentro | Las guardias no son encuentros; las cubren tutores, no necesariamente el profesor del slot |
| Generación HTML | String template server-side en el service | Render del lado frontend | El HTML se pega en el aula virtual (sistema externo); debe ser auto-contenido |
| Permiso único | `encuentros:gestionar` para todo | Permisos separados por sub-recurso | Suficiente para el alcance; se puede granular después si es necesario |
| Export guardias | CSV generado por endpoint | Report builder externo | Simple, no requiere infraestructura adicional, el volumen es bajo |

## Risks / Trade-offs

- **[R1] Generación masiva de instancias**: un slot con 52 semanas genera 52 filas. Para cientos de materias es trivial. Sin riesgo real.
- **[R2] Edición concurrente de instancias**: dos docentes editando la misma instancia. El último write gana (optimistic lock no implementado). Aceptable dado que típicamente un solo profesor edita por materia.
- **[R3] HTML de aula virtual sin estilos**: el bloque generado es HTML plano sin CSS. El LMS destino debe aplicar sus propios estilos.
- **[R4] Guardias sin validación de solapamiento**: un tutor podría registrar dos guardias en el mismo horario. Se deja como mejora futura.
