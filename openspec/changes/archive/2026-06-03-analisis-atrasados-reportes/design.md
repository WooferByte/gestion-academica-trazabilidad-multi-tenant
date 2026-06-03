## Context

C-11 es el primer change puramente analítico del proyecto: consume datos existentes (Calificacion, UmbralMateria, EntradaPadron) sin crear nuevos modelos ni migraciones. Se apoya en C-10 (calificaciones + umbral) que ya está completado.

El módulo es 100% READ-ONLY: no escribe en la BD, solo consulta y computa. El permiso `atrasados:ver` protege todos los endpoints.

## Goals / Non-Goals

**Goals:**
- Cómputo determinístico de alumnos atrasados contra umbral configurado (RN-06)
- Ranking de alumnos por actividades aprobadas (RN-09)
- Reportes rápidos por materia con métricas consolidadas
- Nota final agrupada por alumno
- Export CSV de TPs sin corregir (RN-07/08)
- Monitor general (coordinación/admin) con filtros: materia, comisión, regional, búsqueda por alumno
- Monitor de seguimiento con filtros por tutor/profesor y coordinación/admin con rango de fechas
- Tests con DB real cubriendo cada endpoint

**Non-Goals:**
- No escribir datos (ni Calificacion, ni UmbralMateria, ni nuevos modelos)
- No UI ni frontend (endpoints puramente API)
- No worker ni cola
- No caching de resultados (cada consulta computa en vivo)

## Decisions

1. **Cálculo en Services, no en SQL**
   - Los queries traen datos crudos desde el repositorio; la lógica de negocio (determinar "atrasado", ranking, nota final) se computa en Python en el Service.
   - Contras: más memoria para conjuntos grandes. Pros: testeable, modificable, sin acoplamiento a dialecto SQL.

2. **Repositorio único de solo lectura `AnalisisRepository`**
   - Agrupa todas las queries de agregación del módulo analítico (join Calificacion + EntradaPadron + UmbralMateria).
   - No reusa `CalificacionRepository` porque las queries de análisis tienen estructura distinta (agregaciones por alumno, no por materia).

3. **Endpoint por funcionalidad, no un solo endpoint genérico**
   - `GET /api/analisis/atrasados` — alumnos atrasados
   - `GET /api/analisis/ranking` — ranking de aprobadas
   - `GET /api/analisis/reportes-rapidos` — métricas consolidadas
   - `GET /api/analisis/notas-finales` — notas finales agrupadas
   - `GET /api/analisis/tps-sin-corregir` — exportar listado (CSV)
   - `GET /api/analisis/monitor-general` — monitor transversal
   - `GET /api/analisis/monitor-seguimiento` — monitor filtrado con rango de fechas
   - Cada endpoint devuelve JSON por defecto; los de export aceptan `?format=csv`

4. **Definición de "alumno atrasado" (RN-06)**
   - Se considera atrasado si tiene al menos una actividad donde: (a) no existe calificación registrada, o (b) la nota numérica es menor al umbral configurado, o (c) la nota textual no está en el conjunto de valores aprobatorios.
   - El umbral se resuelve en este orden: (1) UmbralMateria de la asignación del docente → (2) 60% default.

5. **Ranking (RN-09)**
   - Solo incluye alumnos con al menos una actividad aprobada.
   - Orden descendente por cantidad de aprobadas; desempate alfabético por apellido+nombre.

6. **Nota final agrupada**
   - El request especifica qué actividades incluir (por nombre). El sistema promedia las notas numéricas de esas actividades por alumno.
   - Actividades sin nota numérica se excluyen del promedio.

7. **Export CSV**
   - Los endpoints de export (`tps-sin-corregir`, `monitor-general`) responden con `Content-Type: text/csv` cuando `?format=csv`.
   - Reusan la misma lógica de cálculo que los endpoints JSON, solo cambia el serializador.

8. **Multi-tenancy**
   - Todos los queries filtran por `tenant_id` del usuario autenticado (heredado del repositorio base).
   - Los monitores de tutor/profesor además filtran por las materias donde tienen asignación activa.

## Risks / Trade-offs

- [Rendimiento en monitores generales] → Los joins entre Calificacion y EntradaPadron pueden ser pesados para tenants grandes. Mitigación: índices existentes `ix_calificaciones_materia_cohorte` cubren el filtro principal. Si se necesario, index compuesto adicional en `(tenant_id, materia_id, cohorte_id)`.
- [Cálculo en Python vs SQL] → Para conjuntos >10k calificaciones, calcular atrasados en Python puede ser más lento que una query SQL. Trade-off aceptado por testabilidad. Si es necesario optimizar, se puede mover a una función DB materializada en C-XX futuro.
- [Sin paginación en V1] → Los endpoints devuelven listas completas. Si un tenant tiene >500 alumnos en una materia, puede necesitar paginación. Se agrega en iteración si emerge.
