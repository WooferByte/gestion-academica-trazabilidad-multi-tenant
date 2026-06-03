## Context

Activia-trace no dispone de un mecanismo de comunicación interna tipo tablón de avisos. No existe modelo `Aviso` ni `AcknowledgmentAviso`. La KB define el dominio en E13, F3.5, RN-18/19/20 y FL-09. Se requiere implementar desde cero: modelos, repositorio, servicio, schemas, router, migración y tests.

C-06 (Estructura académica) ya está completado, por lo que las entidades `Carrera`, `Cohorte`, `Materia` existen y están disponibles para scoping por contexto.

El tenant se resuelve del JWT autenticado. La identidad del usuario (`usuario_id`, `rol`, `cohorte_ids`) proviene de la sesión, nunca del request.

## Goals / Non-Goals

**Goals:**
- Modelo `Aviso` con alcance (Global/PorMateria/PorCohorte/PorRol), severidad (Info/Advertencia/Crítico), vigencia, orden, activo/inactivo, requiere_ack
- Modelo `AcknowledgmentAviso` con aviso_id, usuario_id, confirmado_at
- ABM de avisos con permiso `avisos:publicar` (COORDINADOR, ADMIN)
- Visualización de avisos activos filtrados por: tenant, rol del usuario, cohorte(s) del usuario, ventana de vigencia
- Confirmación de lectura: usuario hace POST a `/avisos/{id}/ack`, se crea registro en `AcknowledgmentAviso`
- Contadores derivados: total_visualizados = COUNT(AcknowledgmentAviso) por aviso
- Orden de presentación por `orden` ASC, luego `inicio_vigencia` DESC
- Migración Alembic 012 con tablas `aviso` y `acknowledgment_aviso`
- Tests: filtrado por scope, ventana de vigencia, acuse, orden por prioridad, permisos

**Non-Goals:**
- Notificaciones push ni emails al publicar un aviso
- Edición de avisos ya publicados (solo activar/desactivar)
- Frontend del tablón de avisos (se construye en change posterior)
- Avisos programados con publicación diferida automática
- Categorización jerárquica de avisos

## Decisions

### 1. Scope matching vía query dinámica

| Alternativa | Veredicto |
|-------------|-----------|
| Query con CASE/OR por alcance | ✅ Elegido. Única query parametrizada. Simple, eficiente con índices compuestos |
| Post-filter en Python | Descartado. Escala mal con muchos avisos. Rompe paginación |

Se construye una única query SQLAlchemy que aplica filtros condicionales según el alcance:
- `Global`: sin filtro adicional
- `PorRol`: WHERE `rol_destino` = ?
- `PorMateria`: WHERE `materia_id` IN (materias del usuario)
- `PorCohorte`: WHERE `cohorte_id` IN (cohortes del usuario)

### 2. Contadores derivados (no desnormalizados)

| Alternativa | Veredicto |
|-------------|-----------|
| COUNT desde AcknowledgmentAviso | ✅ Elegido. Consistencia garantizada, sin riesgo de desincronización |
| Columna contador en Aviso | Descartado. Inconsistencia potencial, requiere triggers o actualizaciones explícitas |

El endpoint GET /avisos incluye `total_acks` y `user_acked` (bool) como campos calculados.

### 3. Soft delete sobre Aviso, hard delete sobre AcknowledgmentAviso

| Alternativa | Veredicto |
|-------------|-----------|
| Soft delete en Aviso, sin soft delete en Acknowledgment | ✅ Elegido. Avisos se "eliminan" desactivando (`activo=false`). Acuses son datos de auditoría sin baja lógica |
| Soft delete en ambos | Descartado. Acknowledgment es append-only, no tiene sentido borrarlo |

El modelo `Aviso` usa el mixin `SoftDeleteMixin` existente. `AcknowledgmentAviso` es append-only (no se elimina, no se modifica).

### 4. Orden por `orden` ASC, luego `inicio_vigencia` DESC

La prioridad manual (campo `orden`) determina el orden principal. A igual prioridad, los más recientes aparecen primero. Esto permite fijar avisos importantes al tope sin depender de la fecha.

### 5. Validación de vigencia vía DB query

El filtro `WHERE inicio_vigencia <= now() AND fin_vigencia >= now()` se aplica en la query del repositorio, no en el servicio ni en Python, garantizando que la vista del usuario siempre respeta la ventana sin riesgo de datos desactualizados en caché.

## Risks / Trade-offs

- **Query de scope con OR/IN múltiples puede degradar**: mitigación → índice compuesto `(tenant_id, activo, inicio_vigencia, fin_vigencia, alcance)` y evaluar con EXPLAIN ANALYZE.
- **Sin notificaciones, los avisos sólo se ven si el usuario entra al tablón**: aceptado para MVP. Futuro: badge de avisos no leídos.
- **Acknowledgment es append-only sin posibilidad de revocación**: aceptado. Si un usuario confirma por error, no hay deshacer (dato de auditoría).
