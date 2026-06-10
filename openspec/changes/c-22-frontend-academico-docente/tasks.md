## 1. API Endpoint Services

- [x] 1.1 Create `api/endpoints/calificaciones.ts` — importar preview, confirmar, finalización
- [x] 1.2 Create `api/endpoints/umbrales.ts` — GET/PUT umbral
- [x] 1.3 Create `api/endpoints/analisis.ts` — atrasados, ranking, notas-finales, tps-sin-corregir, monitores, reportes-rapidos
- [x] 1.4 Create `api/endpoints/comunicaciones.ts` — preview, send, lote, aprobar-lote, cancelar, tracking
- [x] 1.5 Create `api/endpoints/padron.ts` — importar preview/confirmar, vaciar
- [x] 1.6 Add API response types to `api/types.ts` for all academic endpoints

## 2. Shared Academic Infrastructure

- [x] 2.1 Create `features/academico/types/` with shared TypeScript interfaces (Comision, KPIReporte, AlumnoAtrasado, Actividad, Comunicacion, etc.)
- [x] 2.2 Create `features/academico/hooks/useComisionSelector.ts` — fetch docente's assigned comisiones
- [x] 2.3 Create `features/academico/hooks/useBreadcrumb.ts` — build breadcrumb path from URL params
- [x] 2.4 Create `utils/exportCsv.ts` — JSON-to-CSV utility with BOM for Excel

## 3. Comisión Dashboard (frontend-comision)

- [x] 3.1 Create `features/academico/comision/pages/ComisionSelectorPage.tsx` — cascading materia+cohorte selector
- [x] 3.2 Create `features/academico/comision/pages/ComisionDashboardPage.tsx` — KPI cards + action menu
- [x] 3.3 Create `features/academico/comision/hooks/useComisionKPIs.ts` — fetch reportes-rapidos via TanStack Query
- [x] 3.4 Create `features/academico/comision/components/KpiCard.tsx` — individual KPI display card with loading state
- [x] 3.5 Create `features/academico/comision/components/ActionMenu.tsx` — permission-filtered action buttons grid

## 4. Importación (frontend-importacion)

- [x] 4.1 Create `features/academico/importacion/pages/ImportarPage.tsx` — tabbed import page with step wizard
- [x] 4.2 Create `features/academico/importacion/hooks/useFileUpload.ts` — multipart upload state machine hook
- [x] 4.3 Create `features/academico/importacion/hooks/useImportarCalificaciones.ts` — calificaciones mutations
- [x] 4.4 Create `features/academico/importacion/hooks/useImportarPadron.ts` — padrón mutations
- [x] 4.5 Create `features/academico/importacion/hooks/useVaciarMateria.ts` — vaciar mutation with confirmation
- [x] 4.6 Create `features/academico/importacion/components/UploadStep.tsx` — file input + upload trigger
- [x] 4.7 Create `features/academico/importacion/components/PreviewStep.tsx` — parsed activities with checkboxes
- [x] 4.8 Create `features/academico/importacion/components/ConfirmStep.tsx` — confirmation with summary
- [x] 4.9 Create `features/academico/importacion/components/ImportTabs.tsx` — tab switcher (Calificaciones/Padrón/Finalización)

## 5. Umbral Configuración

- [x] 5.1 Create `features/academico/analisis/pages/UmbralPage.tsx` — slider 0-100% with current value display
- [x] 5.2 Create `features/academico/analisis/hooks/useUmbral.ts` — GET/PUT umbral via TanStack Query + mutation

## 6. Análisis — Atrasados (frontend-analisis)

- [x] 6.1 Create `features/academico/analisis/pages/AtrasadosPage.tsx` — table with checkboxes and badges
- [x] 6.2 Create `features/academico/analisis/hooks/useAtrasados.ts` — fetch atrasados via TanStack Query
- [x] 6.3 Create `features/academico/analisis/components/AtrasadosTable.tsx` — sortable table with status badges (RN-06)
- [x] 6.4 Create `features/academico/analisis/components/ComunicarButton.tsx` — activates with selected count, navigates to comunicar

## 7. Análisis — Ranking

- [x] 7.1 Create `features/academico/analisis/pages/RankingPage.tsx` — ordered student list
- [x] 7.2 Create `features/academico/analisis/hooks/useRanking.ts` — fetch ranking via TanStack Query

## 8. Análisis — Notas Finales

- [x] 8.1 Create `features/academico/analisis/pages/NotasFinalesPage.tsx` — activity selector + grade matrix
- [x] 8.2 Create `features/academico/analisis/hooks/useNotasFinales.ts` — fetch notas-finales with activity params
- [x] 8.3 Create `features/academico/analisis/components/ActivitySelector.tsx` — checkbox list for activities
- [x] 8.4 Create `features/academico/analisis/components/GradeMatrix.tsx` — student × activity grid

## 9. Análisis — TPs sin corregir

- [x] 9.1 Create `features/academico/analisis/pages/TpsSinCorregirPage.tsx` — TP table with CSV export
- [x] 9.2 Create `features/academico/analisis/hooks/useTpsSinCorregir.ts` — fetch tps-sin-corregir

## 10. Análisis — Monitores de Seguimiento

- [x] 10.1 Create `features/academico/analisis/pages/MonitorPage.tsx` — role-switched view (tutor vs coordinación)
- [x] 10.2 Create `features/academico/analisis/hooks/useMonitor.ts` — fetch monitor-seguimiento or monitor-general based on role
- [x] 10.3 Create `features/academico/analisis/components/MonitorFilters.tsx` — materia, comisión, search, date range
- [x] 10.4 Create `features/academico/analisis/components/MonitorTable.tsx` — filterable data table with CSV export

## 11. Comunicaciones (frontend-comunicaciones)

- [x] 11.1 Create `features/academico/comunicaciones/pages/ComunicarPage.tsx` — full communication flow page
- [x] 11.2 Create `features/academico/comunicaciones/hooks/useComunicacionPreview.ts` — preview mutation (RN-16)
- [x] 11.3 Create `features/academico/comunicaciones/hooks/useEnviarComunicacion.ts` — send individual mutation
- [x] 11.4 Create `features/academico/comunicaciones/hooks/useEnviarLote.ts` — send batch mutation (RN-17)
- [x] 11.5 Create `features/academico/comunicaciones/hooks/useComunicacionesTracking.ts` — fetch tracking with polling
- [x] 11.6 Create `features/academico/comunicaciones/hooks/useAprobarLote.ts` — approve lote mutation
- [x] 11.7 Create `features/academico/comunicaciones/hooks/useCancelarComunicacion.ts` — cancel mutation
- [x] 11.8 Create `features/academico/comunicaciones/components/MessageComposer.tsx` — textarea + recipient display
- [x] 11.9 Create `features/academico/comunicaciones/components/PreviewPanel.tsx` — rendered preview with send button
- [x] 11.10 Create `features/academico/comunicaciones/components/TrackingTable.tsx` — status badges with auto-refresh (RN-15)
- [x] 11.11 Create `features/academico/comunicaciones/components/LoteApprovalPanel.tsx` — pending lotes with approve/reject

## 12. Routing & Menu

- [x] 12.1 Add new routes to `RouterProvider.tsx` — all academico nested routes with lazy-loaded pages
- [x] 12.2 Update `menu.service.ts` — update "Académico" section paths and children
- [x] 12.3 Add permission checks to route declarations via ProtectedRoute's requiredPermission

## 13. Tests

- [x] 13.1 Write tests for `utils/exportCsv.ts`
- [x] 13.2 Write tests for API endpoint functions (calificaciones, umbrales, analisis, comunicaciones, padron)
- [x] 13.3 Write tests for shared hooks (useComisionSelector, useBreadcrumb)
- [x] 13.4 Write component tests for KpiCard, ActionMenu, UploadStep, AtrasadosTable, ComunicarButton, TrackingTable
