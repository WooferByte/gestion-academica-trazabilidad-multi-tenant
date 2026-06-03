## 1. Schemas — Nuevos DTOs para operaciones de equipo

- [x] 1.1 Crear `AsignacionMasivaRequest` con usuario_ids, materia_id, carrera_id, cohorte_id, rol, comisiones, desde, hasta
- [x] 1.2 Crear `ClonarEquipoRequest` con origen y destino (materia_id, carrera_id, cohorte_id, desde, hasta)
- [x] 1.3 Crear `VigenciaEquipoRequest` con materia_id, carrera_id, cohorte_id, desde, hasta (todos opcionales excepto materia_id)
- [x] 1.4 Crear `ExportRow` schema para filas del CSV

## 2. Repository — Nuevos métodos en AsignacionRepository

- [x] 2.1 Implementar `create_bulk(entries: list[dict])` — inserta múltiples asignaciones de una vez
- [x] 2.2 Implementar `clone_vigentes(origen: dict, destino: dict)` — busca vigentes en origen, inserta copias en destino
- [x] 2.3 Implementar `update_vigencia_bulk(materia_id, carrera_id, cohorte_id, desde, hasta)` — update masivo de fechas
- [x] 2.4 Implementar `list_for_export(materia_id, carrera_id, cohorte_id)` — query plana con joins para exportación

## 3. Service — Nuevos métodos en AsignacionService

- [x] 3.1 Implementar `mis_equipos(usuario_id, filtros)` — delega a repo filtrando por usuario autenticado
- [x] 3.2 Implementar `asignacion_masiva(data: AsignacionMasivaRequest)` — valida usuarios existen, llama create_bulk, emite auditoría
- [x] 3.3 Implementar `clonar_equipo(data: ClonarEquipoRequest)` — valida origen != destino, llama clone_vigentes, emite auditoría
- [x] 3.4 Implementar `modificar_vigencia(data: VigenciaEquipoRequest)` — valida que existan asignaciones, llama update_vigencia_bulk, emite auditoría
- [x] 3.5 Implementar `exportar_equipo(materia_id, carrera_id, cohorte_id)` — retorna iterable de dicts para CSV

## 4. Router — Nuevo `/api/v1/equipos`

- [x] 4.1 Crear `backend/app/api/v1/routers/equipos.py` con prefix `/api/v1/equipos`
- [x] 4.2 Endpoint `GET /mis-equipos` (solo auth) → AsignacionService.mis_equipos
- [x] 4.3 Endpoint `POST /asignacion-masiva` (permiso `equipos:asignar`) → service.asignacion_masiva
- [x] 4.4 Endpoint `POST /clonar` (permiso `equipos:asignar`) → service.clonar_equipo
- [x] 4.5 Endpoint `PATCH /vigencia` (permiso `equipos:asignar`) → service.modificar_vigencia
- [x] 4.6 Endpoint `GET /exportar` (permiso `equipos:asignar`) → StreamingResponse CSV
- [x] 4.7 Registrar router en `app/main.py` y `app/api/v1/routers/__init__.py`

## 5. Tests

- [x] 5.1 Test de mis-equipos: fixture con PROFESOR asignado, verifica filtros y vigencia
- [x] 5.2 Test de asignación masiva exitosa con 3 docentes
- [x] 5.3 Test de asignación masiva con usuario inexistente → 422 + rollback
- [x] 5.4 Test de clonado entre cohortes con asignaciones vigentes
- [x] 5.5 Test de clonado con origen sin vigentes → lista vacía
- [x] 5.6 Test de modificación de vigencia en bloque
- [x] 5.7 Test de modificación de vigencia con equipo inexistente → 404
- [x] 5.8 Test de exportación CSV con datos
- [x] 5.9 Test de exportación CSV sin resultados → solo headers
- [x] 5.10 Test de permisos: endpoints de escritura rechazan sin `equipos:asignar`
