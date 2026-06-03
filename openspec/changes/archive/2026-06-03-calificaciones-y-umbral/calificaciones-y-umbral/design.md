## Context

C-09 dejó el padrón versionado (VersionPadron + EntradaPadron). Ahora se necesita poblar calificaciones por alumno desde archivos exportados del LMS y configurar umbrales de aprobación. `aprobado` es derivado (no se almacena). El patrón de import sigue el mismo esquema de C-09: preview → confirm.

## Goals / Non-Goals

**Goals:**
- Modelos Calificacion y UmbralMateria con multi-tenancy y soft delete
- Import de calificaciones xlsx/csv con detección de columnas numéricas y textuales
- Preview con actividades detectadas + selección del usuario
- Confirmación que persiste calificaciones y audita con CALIFICACIONES_IMPORTAR
- Configuración de umbral por materia×asignación (default 60%)
- `aprobado` campo derivado: nota_numerica >= umbral o nota_textual ∈ valores_aprobatorios
- Migración Alembic 008
- Import de reporte de finalización con cruce contra calificaciones

**Non-Goals:**
- Cómputo de ranking o alumnos atrasados (eso es C-11)
- Comunicación con alumnos (C-12)
- UI frontend (C-21/C-22)

## Decisions

1. **`aprobado` como propiedad del schema (no columna)**: Se calcula al serializar la Calificacion. Evita datos desactualizados si cambia el umbral. El schema Pydantic tiene un `@field_validator` o `@computed_field` que recibe el umbral como parámetro.

2. **Import en dos fases idéntico a padrón**: `preview_import` parsea el archivo, detecta actividades, devuelve preview. `confirm_import` recibe la selección del usuario y persiste. Esto mantiene consistencia con el flujo de C-09.

3. **Umbral por Asignacion × Materia**: La entidad UmbralMateria se relaciona con Asignacion (docente+materia+cohorte). Si no existe configuración, se usa default 60% del tenant.

4. **Servicio separado**: `CalificacionesService` en lugar de extender PadronService. Cada dominio tiene su propio service, aunque reusan repositorios de entrada_padron para validar pertenencia.

5. **openpyxl ya disponible**: La dependencia se agregó en C-09 para el padrón. Se reusa para calificaciones.

6. **Columnas (Real) para numéricas (RN-01)**: El parser detecta columnas cuyo header termina en `(Real)` como numéricas. El resto se considera textual. Esto es parte del archivo exportado del LMS.

## Risks / Trade-offs

- **Cambio de umbral invalida aprobados históricos**: Si un docente cambia el umbral después de importar, las calificaciones existentes cambian su estado aprobado. Esto es intencional (el umbral es una configuración activa, no un snapshot). → Mitigación: audit trail registra el cambio de umbral.
- **Archivos LMS variables**: El formato de exportación del LMS puede variar. → Mitigación: preview permite al usuario verificar antes de confirmar.
- **Rendimiento con muchas calificaciones**: Bulk insert optimizado con `insert().execute()` en lote. Preview calcula en memoria.
