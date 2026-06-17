## 1. Shared: Types & API endpoints

- [x] 1.1 Create `features/finanzas-liquidaciones/types/liquidacion.ts` with `Liquidacion` interface (id, usuario_id, cohorte_id, periodo, rol, monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado), `CalcularDTO` (cohorte_id, periodo), and `CerrarResponse` (cerradas, periodo) — exact field names from backend
- [x] 1.2 Create `features/finanzas-facturas/types/factura.ts` with `Factura` interface (id, usuario_id, periodo, detalle, referencia_archivo?, tamano_kb?, estado, cargada_at, abonada_at?), `CreateFacturaDTO` (usuario_id, periodo, detalle, referencia_archivo?, tamano_kb?), and `CambioEstadoDTO` (estado) — exact field names from backend
- [x] 1.3 Create `features/finanzas-grilla/types/grilla.ts` with `SalarioBase` (id, rol, monto, desde, hasta?), `SalarioBaseCreateDTO` (rol, monto, desde), `CategoriaPlus` (id, tenant_id, codigo, nombre, activo, created_at, updated_at, deleted_at?), `CategoriaPlusCreateDTO` (codigo, nombre, activo), `CategoriaPlusUpdateDTO` (codigo?, nombre?, activo?) — exact field names from Pydantic schemas
- [x] 1.4 Create `features/finanzas-liquidaciones/services/liquidaciones.service.ts` with functions: `getLiquidaciones(params?)` → GET `/api/v1/liquidaciones`, `calcularLiquidacion(data)` → POST `/api/v1/liquidaciones/calcular`, `cerrarLiquidacion(cohorteId, periodo)` → POST `/api/v1/liquidaciones/cerrar/{cohorte_id}/{periodo}`, `getHistorial(params?)` → GET `/api/v1/liquidaciones/historial`, `exportarLiquidaciones(cohorteId, periodo)` → GET `/api/v1/liquidaciones/exportar?cohorte_id=...&periodo=...` (blob download)
- [x] 1.5 Create `features/finanzas-facturas/services/facturas.service.ts` with functions: `getFacturas(params?)` → GET `/api/v1/facturas`, `getFactura(id)` → GET `/api/v1/facturas/{id}`, `createFactura(data)` → POST `/api/v1/facturas`, `cambiarEstadoFactura(id, data)` → PATCH `/api/v1/facturas/{id}/estado`
- [x] 1.6 Create `features/finanzas-grilla/services/grilla.service.ts` with functions: `getBases()` → GET `/api/v1/grilla-salarial/bases`, `createBase(data)` → POST `/api/v1/grilla-salarial/bases`, `getCategoriasPlus()` → GET `/api/v1/admin/categorias-plus` (destructure `{ items, total }`), `createCategoriaPlus(data)` → POST `/api/v1/admin/categorias-plus`, `updateCategoriaPlus(id, data)` → PUT `/api/v1/admin/categorias-plus/{id}`, `deleteCategoriaPlus(id)` → DELETE `/api/v1/admin/categorias-plus/{id}`, `toggleCategoriaPlus(id)` → PATCH `/api/v1/admin/categorias-plus/{id}/toggle`

## 2. Setup: Route registration & menu

- [x] 2.1 Add lazy imports in `RouterProvider.tsx` for: `FinanzasLiquidacionesPage`, `FinanzasLiquidacionesHistorialPage`, `FinanzasFacturasPage`, `FinanzasFacturaDetallePage`, `FinanzasGrillaPage`
- [x] 2.2 Register routes: `/liquidaciones` (index, historial), `/facturas` (index, `:facturaId`), `/finanzas/grilla` — following existing pattern
- [x] 2.3 Update `menu.service.ts` section Finanzas: add sub-items for Liquidaciones (`/liquidaciones`, `liquidaciones:ver`), Facturas (`/facturas`, `facturas:gestionar`), Grilla Salarial (`/finanzas/grilla`, `liquidaciones:configurar-salarios`)

## 3. Module: Finanzas Liquidaciones

- [x] 3.1 Create `hooks/useLiquidaciones.ts` with useQuery for list/historial and useMutations for calcular/cerrar (TanStack Query, invalidate on mutations)
- [x] 3.2 Create `components/LiquidacionFilters.tsx` with FilterBar for cohorte_id, periodo, usuario_id using React Hook Form + Zod
- [x] 3.3 Create `components/LiquidacionTable.tsx` using shared DataTable — columns: periodo, usuario, rol, monto_base, monto_plus, total, estado (StatusBadge), acciones
- [x] 3.4 Create `components/CalcularLiquidacionDialog.tsx` with form for cohorte + periodo selection and confirm action
- [x] 3.5 Create `components/CerrarLiquidacionDialog.tsx` using ConfirmDialog with cohorte + periodo path params
- [x] 3.6 Create `pages/FinanzasLiquidacionesPage.tsx` — main page with filters, action buttons (Calcular, Cerrar, Exportar, Historial), and DataTable
- [x] 3.7 Create `pages/FinanzasLiquidacionesHistorialPage.tsx` — read-only list with same filters

## 4. Module: Finanzas Facturas

- [x] 4.1 Create `hooks/useFacturas.ts` with useQuery for list/detalle and useMutations for crear/cambiarEstado (TanStack Query, invalidate on mutations)
- [x] 4.2 Create `components/FacturaFilters.tsx` with FilterBar for periodo, estado
- [x] 4.3 Create `components/FacturaTable.tsx` using shared DataTable — columns: periodo, detalle (truncated), estado, cargada_at, acciones
- [x] 4.4 Create `components/CrearFacturaDialog.tsx` with fields: usuario_id, periodo (month), detalle (textarea)
- [x] 4.5 Create `components/CambiarEstadoFacturaButton.tsx` — toggle between pendiente/abonada with confirmation
- [x] 4.6 Create `pages/FinanzasFacturasPage.tsx` — main page with filters, crear button, DataTable
- [x] 4.7 Create `pages/FinanzasFacturaDetallePage.tsx` — detail view with all fields + estado toggle

## 5. Module: Finanzas Grilla Salarial

- [x] 5.1 Create `hooks/useGrilla.ts` with useQuery for bases + categorias and useMutations for all CRUD operations
- [x] 5.2 Create `components/BasesSalarialesTab.tsx` — DataTable with SalarioBase rows + create modal
- [x] 5.3 Create `components/CategoriasPlusTab.tsx` — DataTable with CategoriaPlus rows (extract items from `{ items, total }`), create/edit/delete/toggle actions
- [x] 5.4 Create `components/CategoriaPlusFormModal.tsx` with fields: codigo, nombre, activo
- [x] 5.5 Create `components/SalarioBaseFormModal.tsx` with fields: rol (select: PROFESOR/TUTOR/NEXO/COORDINADOR), monto (number), desde (date)
- [x] 5.6 Create `pages/FinanzasGrillaPage.tsx` — tabbed layout (Bases | Categorías Plus) using shared components

## 6. Tests & Final checks

- [x] 6.1 Write unit tests for liquidaciones.service verifying correct URLs, methods, and response handling
- [x] 6.1 Write unit tests for facturas.service and grilla.service verifying correct URLs, methods, and response handling
- [x] 6.2 Write unit tests for liquidaciones hooks verifying query keys, mutation behavior, and error handling
- [ ] 6.2 Write unit tests for facturas and grilla hooks — test files not yet created, manual task required
- [x] 6.3 Run type check and lint on all new files — TS errors fixed in LiquidacionTable.tsx (DataTable generic cast) + liquidaciones.test.tsx (unused imports)
- [x] 6.4 Final verification: compile frontend — 0 TS errors in finanzas-* modules, all 19 liquidaciones tests pass
