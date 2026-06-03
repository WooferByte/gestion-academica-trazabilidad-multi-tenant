## 1. Modelos y migración

- [x] 1.1 Crear modelo SQLAlchemy `SlotEncuentro` con campos: id, tenant_id, asignacion_id, materia_id, titulo, hora, dia_semana (enum), fecha_inicio, cant_semanas, fecha_unica (nullable), meet_url, vig_desde, vig_hasta, created_at, updated_at, deleted_at
- [x] 1.2 Crear modelo SQLAlchemy `InstanciaEncuentro` con campos: id, tenant_id, slot_id (nullable), materia_id, fecha, hora, titulo, estado (enum: Programado|Realizado|Cancelado), meet_url, video_url (nullable), comentario, created_at, updated_at, deleted_at
- [x] 1.3 Crear modelo SQLAlchemy `Guardia` con campos: id, tenant_id, asignacion_id, materia_id, carrera_id, cohorte_id, dia (enum), horario, estado (enum: Pendiente|Realizada|Cancelada), comentarios, creada_at, updated_at, deleted_at
- [x] 1.4 Crear migración Alembic 010 con las tres tablas, índices y FKs correspondientes
- [x] 1.5 Registrar modelos en `__init__` de modelos y en la configuración de Alembic

## 2. Repositories

- [x] 2.1 Crear `SlotEncuentroRepository` con métodos: create, get_by_id, list_by_materia (scoped por tenant)
- [x] 2.2 Crear `InstanciaEncuentroRepository` con métodos: create, get_by_id, update, list (con filtros por materia_id, desde, hasta, estado, slot_id), list_by_materias (para vista global de coordinador)
- [x] 2.3 Crear `GuardiaRepository` con métodos: create, get_by_id, update, list (con filtros), list_by_usuario (para TUTOR), export_csv (query con los mismos filtros)

## 3. Services

- [x] 3.1 Implementar `SlotEncuentroService.create_slot()`: crea el slot y genera N instancias según cant_semanas (RN-13); si cant_semanas=0 no genera instancias
- [x] 3.2 Implementar lógica de generación de instancias: calcular fechas sucesivas respetando dia_semana desde fecha_inicio, cada instancia con estado Programado
- [x] 3.3 Implementar `InstanciaEncuentroService.create_unique()`: crear instancia sin slot padre
- [x] 3.4 Implementar `InstanciaEncuentroService.update()`: validar tenant, actualizar campos editables (estado, meet_url, video_url, comentario)
- [x] 3.5 Implementar `InstanciaEncuentroService.generate_html()`: generar fragmento HTML con tabla de encuentros por materia
- [x] 3.6 Implementar `InstanciaEncuentroService.list_with_filters()`: con paginación, filtro por tenant, scope por rol (COORDINADOR ve todo, PROFESOR solo sus materias)
- [x] 3.7 Implementar `GuardiaService.create()`: crear guardia con estado Pendiente, scoped por tenant
- [x] 3.8 Implementar `GuardiaService.list_with_filters()`: paginado, scope por rol (COORDINADOR ve todo, TUTOR solo sus guardias)
- [x] 3.9 Implementar `GuardiaService.export_csv()`: query filtrada + respuesta CSV
- [x] 3.10 Implementar `GuardiaService.update_state()`: cambiar estado y comentarios

## 4. Routers y permisos

- [x] 4.1 Crear router `encuentros_slots.py` con endpoints: POST /slots, GET /slots, GET /slots/{id}
- [x] 4.2 Crear router `encuentros_instancias.py` con endpoints: POST /instancias, GET /instancias, GET /instancias/{id}, PATCH /instancias/{id}, GET /instancias?html=true
- [x] 4.3 Crear router `guardias.py` con endpoints: POST /guardias, GET /guardias, GET /guardias/{id}, PATCH /guardias/{id}, GET /guardias/export
- [x] 4.4 Agregar permiso `encuentros:gestionar` al catálogo de permisos
- [x] 4.5 Aplicar guard `require_permission("encuentros:gestionar")` en todos los endpoints
- [x] 4.6 Registrar routers en la aplicación FastAPI con prefijo `/api/v1`

## 5. Tests

- [x] 5.1 Test: crear slot recurrente con 4 semanas genera 4 instancias con fechas correctas
- [x] 5.2 Test: crear slot con cant_semanas=0 no genera instancias
- [x] 5.3 Test: crear encuentro único sin slot_id
- [x] 5.4 Test: editar instancia — cambiar estado a Realizado
- [x] 5.5 Test: editar instancia — agregar video_url
- [x] 5.6 Test: editar instancia inexistente retorna 404
- [x] 5.7 Test: generar HTML con encuentros programados
- [x] 5.8 Test: generar HTML sin encuentros retorna mensaje informativo
- [x] 5.9 Test: vista global — coordinador ve todas las instancias
- [x] 5.10 Test: vista global — profesor ve solo sus materias
- [x] 5.11 Test: registrar guardia como TUTOR
- [x] 5.12 Test: registrar guardia con datos faltantes retorna 422
- [x] 5.13 Test: consultar guardias — coordinador ve todas
- [x] 5.14 Test: consultar guardias — tutor ve solo las suyas
- [x] 5.15 Test: exportar guardias a CSV
- [x] 5.16 Test: exportar guardias sin resultados retorna CSV con cabecera
- [x] 5.17 Test: actualizar estado de guardia a Realizada
- [x] 5.18 Test: permiso — endpoint sin token retorna 401
