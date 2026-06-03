## 1. Modelos y Migración

- [x] 1.1 Crear modelo `Calificacion` con tenant_id, entrada_padron_id, materia_id, actividad, nota_numerica, nota_textual, origen (enum Importado|Manual), importado_at, soft delete
- [x] 1.2 Crear modelo `UmbralMateria` con tenant_id, asignacion_id, materia_id, umbral_pct (default 60), valores_aprobatorios (JSONB), soft delete
- [x] 1.3 Generar migración Alembic 008 con tablas `calificacion` y `umbral_materia`, índices, FKs

## 2. Schemas Pydantic

- [x] 2.1 Crear `CalificacionResponse` con campo derivado `aprobado` (computed: nota_numerica >= umbral o nota_textual ∈ valores_aprobatorios)
- [x] 2.2 Crear schemas de import: `CalificacionImportPreviewRequest`, `ActividadDetectada`, `CalificacionPreviewResponse`, `CalificacionConfirmRequest`, `CalificacionConfirmResponse`
- [x] 2.3 Crear schemas de umbral: `UmbralMateriaCreate`, `UmbralMateriaUpdate`, `UmbralMateriaResponse`
- [x] 2.4 Crear schemas de reporte finalización: `ReporteFinalizacionPreviewResponse`, `EntregaSinCorregir`

## 3. Repositorios

- [x] 3.1 Crear `CalificacionRepository` con métodos: bulk_create, get_by_materia, get_by_entrada_padron, soft_delete_by_materia
- [x] 3.2 Crear `UmbralMateriaRepository` con métodos: get_by_asignacion, upsert, get_by_materia

## 4. Servicio de Calificaciones

- [x] 4.1 Implementar `_parse_calificaciones_xlsx` y `_parse_calificaciones_csv` con detección de columnas numéricas (RN-01: sufijo `(Real)`) y textuales (RN-02)
- [x] 4.2 Implementar `preview_import`: parsea archivo, detecta actividades, devuelve `CalificacionPreviewResponse` con actividades detectadas y total filas
- [x] 4.3 Implementar `confirm_import`: recibe selección de actividades, persiste Calificaciones vinculadas a EntradaPadron, audita con `CALIFICACIONES_IMPORTAR`
- [x] 4.4 Implementar `import_reporte_finalizacion`: parsea reporte, cruza contra Calificaciones existentes, devuelve tabla de entregas sin corregir (RN-07, RN-08)

## 5. Servicio de Umbral

- [x] 5.1 Implementar `configurar_umbral`: crea o actualiza UmbralMateria para una asignación, valida permisos
- [x] 5.2 Implementar `obtener_umbral`: recupera umbral configurado o default 60%
- [x] 5.3 Integrar derivación de `aprobado` en `CalificacionResponse` usando umbral de la materia

## 6. Router y Endpoints

- [x] 6.1 Crear `calificaciones_router.py` con POST `/calificaciones/preview`, POST `/calificaciones/confirmar`, POST `/calificaciones/reporte-finalizacion`
- [x] 6.2 Crear `umbral_router.py` con GET `/umbral/{materia_id}`, PUT `/umbral/{materia_id}`
- [x] 6.3 Registrar routers en la aplicación FastAPI

## 7. Tests

- [x] 7.1 Test de derivación de `aprobado`: numérica >= umbral, numérica < umbral, textual aprobatorio, textual no aprobatorio
- [x] 7.2 Test de preview import: columnas numéricas detectadas, columnas textuales, preview con actividades
- [x] 7.3 Test de confirmación import: persiste calificaciones, audita con CALIFICACIONES_IMPORTAR
- [x] 7.4 Test de selección de actividades: import parcial, solo actividades seleccionadas
- [x] 7.5 Test de umbral: crear, actualizar, default 60%, afecta derivación de aprobado
- [x] 7.6 Test de reporte finalización: cruce contra calificaciones, solo textuales (RN-08), entregas sin corregir
