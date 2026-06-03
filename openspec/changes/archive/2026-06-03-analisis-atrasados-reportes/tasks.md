## 1. Scaffolding y configuración

- [ ] 1.1 Crear `backend/app/repositories/analisis_repository.py` con queries de solo lectura (join Calificacion × EntradaPadron × UmbralMateria)
- [ ] 1.2 Crear `backend/app/schemas/analisis.py` con DTOs request/response (AlumnoAtrasado, RankingEntry, ReporteRapido, NotaFinal, TPSinCorregir, MonitorEntry, MonitorSeguimiento)
- [ ] 1.3 Crear `backend/app/services/analisis_service.py` con lógica de cálculo (atrasados, ranking, notas finales, monitores)
- [ ] 1.4 Crear `backend/app/routers/analisis_router.py` con todos los endpoints protegidos por `atrasados:ver`
- [ ] 1.5 Agregar `ANALISIS_CONSULTAR` a `backend/app/core/audit_codes.py`
- [ ] 1.6 Registrar el router en `backend/app/main.py`
- [ ] 1.7 Crear `backend/tests/test_analisis/` con `__init__.py` y `conftest.py` para datos de prueba

## 2. AnalisisRepository — queries de solo lectura

- [ ] 2.1 Implementar `get_calificaciones_con_alumnos(materia_id, cohorte_id)` — join Calificacion + EntradaPadron
- [ ] 2.2 Implementar `get_actividades_por_materia(materia_id, cohorte_id)` — actividades distintas
- [ ] 2.3 Implementar `get_alumnos_por_materia(materia_id, cohorte_id)` — entradas del padrón activo
- [ ] 2.4 Implementar `get_calificaciones_por_tenant()` — para monitor general (todos los alumnos del tenant)
- [ ] 2.5 Implementar `get_calificaciones_por_asignaciones(usuario_id)` — para monitor de seguimiento (solo materias del usuario)

## 3. AnalisisService — lógica de cálculo

- [ ] 3.1 Implementar `calcular_atrasados(materia_id, cohorte_id)` — determina atrasados según RN-06 (actividades faltantes o nota < umbral)
- [ ] 3.2 Implementar `calcular_ranking(materia_id, cohorte_id)` — ranking descendente con mínimo 1 aprobada (RN-09)
- [ ] 3.3 Implementar `calcular_reporte_rapido(materia_id, cohorte_id)` — métricas consolidadas
- [ ] 3.4 Implementar `calcular_notas_finales(materia_id, cohorte_id, actividades)` — promedio por alumno
- [ ] 3.5 Implementar `exportar_tps_sin_corregir(materia_id, cohorte_id)` — cruce reporte vs calificaciones (RN-07/08)
- [ ] 3.6 Implementar `monitor_general(filtros)` — vista transversal con filtros materia/comisión/regional/búsqueda
- [ ] 3.7 Implementar `monitor_seguimiento(usuario_id, filtros)` — vista restringida a materias del usuario + rango de fechas

## 4. Router — endpoints /api/analisis/*

- [ ] 4.1 Implementar `GET /api/analisis/atrasados?materia_id=&cohorte_id=` — devuelve lista de atrasados
- [ ] 4.2 Implementar `GET /api/analisis/ranking?materia_id=&cohorte_id=` — devuelve ranking ordenado
- [ ] 4.3 Implementar `GET /api/analisis/reportes-rapidos?materia_id=&cohorte_id=` — devuelve métricas consolidadas
- [ ] 4.4 Implementar `GET /api/analisis/notas-finales?materia_id=&cohorte_id=&actividades=` — devuelve notas finales por alumno
- [ ] 4.5 Implementar `GET /api/analisis/tps-sin-corregir?materia_id=&cohorte_id=&format=json|csv` — exportación
- [ ] 4.6 Implementar `GET /api/analisis/monitor-general` — monitor transversal con filtros query params
- [ ] 4.7 Implementar `GET /api/analisis/monitor-seguimiento` — monitor filtrado con rango de fechas

## 5. Tests

- [ ] 5.1 Test: atrasados con actividad faltante se detecta como atrasado
- [ ] 5.2 Test: atrasados con nota menor al umbral se detecta como atrasado
- [ ] 5.3 Test: atrasados con nota textual no aprobatoria se detecta como atrasado
- [ ] 5.4 Test: atrasados con todas aprobadas no aparece
- [ ] 5.5 Test: ranking incluye solo alumnos con >=1 aprobada
- [ ] 5.6 Test: ranking ordenado descendente con desempate alfabético
- [ ] 5.7 Test: reporte rápido con métricas correctas
- [ ] 5.8 Test: notas finales promedian actividades seleccionadas
- [ ] 5.9 Test: export CSV de TPs sin corregir
- [ ] 5.10 Test: monitor general filtra por materia
- [ ] 5.11 Test: monitor seguimiento filtra por comisión
- [ ] 5.12 Test: monitor seguimiento con rango de fechas (coordinación)
- [ ] 5.13 Test: 403 sin permiso atrasados:ver
- [ ] 5.14 Test: aislamiento multi-tenant en todos los endpoints
