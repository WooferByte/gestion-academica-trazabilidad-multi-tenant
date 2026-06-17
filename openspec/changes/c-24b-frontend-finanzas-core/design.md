## Context

El backend ya expone 4 módulos REST completos en `/api/v1/liquidaciones`, `/api/v1/facturas`, `/api/v1/admin/categorias-plus` y `/api/v1/grilla-salarial`. El frontend actual tiene una sección Finanzas placeholder en el menú (menu.service.ts línea 213-224). Este change implementa las 3 páginas principales, siguiendo el patrón feature-based usado en C-24a (admin-estructura).

## Goals / Non-Goals

**Goals:**
- Implementar Liquidaciones: listar (con filtros), calcular, cerrar (con confirmación), historial, exportar CSV
- Implementar Facturas: listar (con filtros), crear, detalle, cambiar estado (pendiente/abonada)
- Implementar Grilla Salarial: CRUD de Salarios Base, CRUD de Categorías Plus con toggle/asignación masiva
- Seguir el patrón feature-based: types/ → services/ → hooks/ → components/ → pages/
- Usar las shared components de `admin-estructura/shared/` (DataTable, PageHeader, StatusBadge, ConfirmDialog, FilterBar)
- Sincronizar con los contratos exactos del backend ya verificados

**Non-Goals:**
- No incluir dashboard con KPIs contables (F10.6 separación contable — se hará en change posterior)
- No incluir subida de archivos real en facturas (archivo adjunto es metadata-only en MVP)
- No incluir importación masiva de categorías plus (solo crear one-off y asignación masiva existente)

## Decisions

1. **Rutas**: Se crean 3 grupos de rutas:
   - `/liquidaciones` → listar / calcular / cerrar / historial / exportar
   - `/facturas` → listar / crear / `:id` detalle
   - `/finanzas/grilla` → bases y categorías plus (admin-panel style)

2. **Estructura de módulos**: Cada módulo en su propio feature folder (`finanzas-liquidaciones/`, `finanzas-facturas/`, `finanzas-grilla/`). La grilla combina bases + plus en un mismo módulo porque comparten layout y permisos (`liquidaciones:configurar-salarios`).

3. **Response format**: Cada módulo usa el formato exacto del backend:
   - Liquidaciones: `list[T]` (bare array)
   - Facturas: `list[T]` (bare array)
   - Categorías Plus: `{ items, total }` (wrapped)
   - Grilla Salarial (bases/pluses): `list[T]` (bare array)

4. **HTTP methods**: se copian exactos del backend router decorators (GET/POST/POST/PATCH, etc.)

5. **Filtros**: implementados como query params opcionales vía React Hook Form + FilterBar shared component.

6. **Estado de liquidación**: `abierta` (editable, default) / `cerrada` (inmutable). Al cerrar se usa ConfirmDialog inmutable.

7. **Facturas estados**: `pendiente` → `abonada` (toggle via PATCH con CambioEstadoRequest `{ "estado" }`).

8. **Error handling**: showToast en catch blocks, mutation errors via onError callback.

## Risks / Trade-offs

- **CSV export**: requiere manejar StreamingResponse como blob descargable. El endpoint `/exportar` requiere `cohorte_id` y `periodo` como query params obligatorios.
- **Categorías Plus: { items, total } vs bare array**: riesgo de confusión porque los otros módulos devuelven array directo. Validar el response.data destructurando correctamente.
- **extra='forbid'**: cualquier campo extra en POST/PATCH causa 422. Los types/DTOs deben ser exactos al schema Pydantic.
- **Cerrar liquidación usa path params**: `POST /api/v1/liquidaciones/cerrar/{cohorte_id}/{periodo}` — requiere construcción de URL con segmentos, no query params.
