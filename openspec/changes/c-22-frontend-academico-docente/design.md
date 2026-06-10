## Context

The backend for activia-trace is fully deployed with all academic endpoints (calificaciones, umbrales, análisis, comunicaciones, padrón). The frontend shell (C-21) already provides auth, routing, layout, and UI primitives. The module Académico-Docente is the first functional module to be built — it consumes existing REST APIs without any backend changes.

Existing frontend architecture:
- `trace-app/` — Vite + React 18, feature-based modules at `src/features/{name}/`
- `components/ui/` — Button, Card, Input, Badge, Avatar, Skeleton, Dialog, Toast
- `components/routing/` — ProtectedRoute (with permission check), PublicRoute, LoadingSkeleton
- `api/client.ts` — Axios with JWT refresh rotation + tenant header injection
- `api/endpoints/` — one file per domain (currently only auth.ts)
- `features/auth/` — useAuth context (user, permissions, isAuthenticated)
- `features/shell/` — AppLayout (Sidebar + Topbar), RouterProvider, menu.service.ts
- TanStack Query in App.tsx (staleTime: 5min, retry: 1)

## Goals / Non-Goals

**Goals:**
- Build 9+ frontend pages under `/academico/` that consume existing backend APIs
- Reusable hooks and components for the academic module
- File upload wizard pattern for import flows
- Communication flow with mandatory preview (RN-16)
- Permission-based route guards and menu filtering
- Export CSV for analysis views

**Non-Goals:**
- No backend changes — this is strictly frontend
- No new UI primitives — reuse existing components
- No real-time features — polling or manual refresh only
- No offline support

## Decisions

### 1. Feature Module Structure — `features/academico/` with sub-modules
Use a sub-module per capability inside `features/academico/`:
```
features/academico/
  comision/         → dashboard, KPIs, action menu
  importacion/      → file upload wizard (calificaciones, padrón, finalización)
  analisis/         → atrasados, ranking, notas-finales, tps-sin-corregir, monitores
  comunicaciones/   → preview, envío, tracking, aprobación
  types/            → shared academic types
  hooks/            → shared hooks (useComisionSelector, etc.)
  services/         → API endpoint functions
```
**Rationale**: Matches the existing feature-based pattern, keeps each sub-module focused (<200 LOC per component), and maps 1:1 to the capability specs.

### 2. Route Structure — Nested under existing protected layout
Routes are nested under the existing `<ProtectedRoute>` + `<AppLayout>` in `RouterProvider`:
```
<Route path="academico" element={<ProtectedRoute requiredPermission="..." />}>
  <Route element={<AppLayout />}>
    <Route index element={<ComisionSelectorPage />} />
    <Route path=":materiaId/:cohorteId" element={<ComisionDashboardPage />} />
    <Route path=":materiaId/:cohorteId/importar" element={<ImportarPage />} />
    <Route path=":materiaId/:cohorteId/umbral" element={<UmbralPage />} />
    <Route path=":materiaId/:cohorteId/atrasados" element={<AtrasadosPage />} />
    <Route path=":materiaId/:cohorteId/ranking" element={<RankingPage />} />
    <Route path=":materiaId/:cohorteId/notas" element={<NotasPage />} />
    <Route path=":materiaId/:cohorteId/comunicar" element={<ComunicarPage />} />
    <Route path=":materiaId/:cohorteId/monitor" element={<MonitorPage />} />
  </Route>
</Route>
```
**Rationale**: URL params (`materiaId`, `cohorteId`) are the natural state carrier for context propagation. Pages read them via `useParams()`.

### 3. API Service Files — One per domain, matching backend modules
Create dedicated endpoint files under `api/endpoints/`:
- `calificaciones.ts` — importar preview/confirmar, listar, finalización
- `umbrales.ts` — GET/PUT umbral
- `analisis.ts` — atrasados, ranking, notas-finales, tps-sin-corregir, monitores
- `comunicaciones.ts` — preview, send, lote, aprobar-lote, cancelar, tracking
- `padron.ts` — importar preview/confirmar, vaciar

### 4. TanStack Query Hooks — `useQuery` for reads, `useMutation` for writes
Each sub-module has a `hooks/` directory with custom hooks wrapping API calls:
- `useComisionKPIs(materiaId, cohorteId)` → `useQuery` for reportes-rapidos
- `useImportarMutation()` → `useMutation` wrapping POST
- `useAtrasados(materiaId, cohorteId)` → `useQuery`
- `useComunicacionPreview()` → `useMutation` (preview is always a POST)
- `useEnviarComunicacion()` → `useMutation`
- `useUmbral(materiaId, cohorteId)` → `useQuery`; `useUmbralMutation()` → `useMutation`
- `useRanking(materiaId, cohorteId)` → `useQuery`
- `useNotasFinales(materiaId, cohorteId, actividades)` → `useQuery`
- `useMonitorSeguimiento()` → `useQuery`
- `useMonitorGeneral()` → `useQuery`

### 5. File Upload Pattern — Multipart form-data with preview step
The import wizard uses a 3-step flow:
1. **Step 1 — Upload**: `<input type="file">` → `FormData` append → `api.post('/importar/preview', formData, { headers: { 'Content-Type': 'multipart/form-data' } })`
2. **Step 2 — Preview**: Display parsed activities with checkboxes; user selects which to import
3. **Step 3 — Confirm**: `api.post('/importar/confirmar', { file_token, selected_actividades })`

A `useFileUpload()` hook manages the state machine: `idle → uploading → preview → confirming → done/error`.

### 6. Communication Flow — Preview first, then send (RN-16)
The communication page enforces:
1. Select recipients (from atrasados table checkboxes, passed via navigation state)
2. Preview message → `POST /api/v1/comunicaciones/preview` → shows rendered preview
3. User confirms → `POST /api/v1/comunicaciones` (individual) or `/lote` (masivo)
4. Tracking view: `GET /api/v1/comunicaciones?lote_id=X` with status badges

The flow uses `useState` for the state machine: `select → preview → confirm → tracking`.

### 7. Menu Configuration — Update existing menu entries
Modify `menu.service.ts` to update paths under "Académico" section to point to `/academico/:materiaId/:cohorteId/*` or the selector page. The top-level "Académico" menu entry stays as a redirect to the comision selector.

### 8. Export CSV — JSON-to-CSV utility
Create a `utils/exportCsv.ts` utility that takes an array of objects and column config, generates CSV with BOM for Excel compatibility, and triggers download via `URL.createObjectURL`.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large page size if all features in one route | Lazy-loaded via React.lazy + Suspense (already in RouterProvider) |
| Upload wizard state loss on refresh | Store `file_token` in URL search params or session storage |
| Communication preview step may frustrate users | Show clear loading state; cache last preview response to allow re-sending without re-preview within same session |
| Permission changes mid-session | Expired permissions handled by 403 interceptor in api/client.ts showing toast + redirect |
| URL params for materiaId/cohorteId could be stale | Components validate via `isValid` on query params; redirect to selector if invalid |
