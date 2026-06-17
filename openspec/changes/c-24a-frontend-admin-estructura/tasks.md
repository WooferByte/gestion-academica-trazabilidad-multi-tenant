## 1. Shared Components (admin-estructura)

- [x] 1.1 Create `features/admin-estructura/` directory structure with `shared/` subfolder
- [x] 1.2 Build `DataTable` component with sorting, pagination, loading skeleton, empty state
- [x] 1.3 Build `SearchInput` component with debounced onChange
- [x] 1.4 Build `StatusBadge` component (activo/inactivo variants)
- [x] 1.5 Build `ConfirmDialog` component for delete/confirm actions
- [x] 1.6 Build `PageHeader` component with title and action button slot
- [x] 1.7 Build `FilterBar` component with date range, select, and input filters
- [x] 1.8 Build `EmptyState` component with icon, message, and optional action
- [x] 1.9 Build type-safe `useDataTable` hook for pagination/sorting state
- [x] 1.10 Write tests for all shared components and hooks

## 2. admin-carreras Module

- [x] 2.1 Create `features/admin-carreras/types/carrera.ts` with Carrera interface and CreateCarreraDTO/UpdateCarreraDTO
- [x] 2.2 Create `features/admin-carreras/services/carreras.service.ts` with all API calls (GET, POST, PUT, DELETE)
- [x] 2.3 Create `features/admin-carreras/hooks/useCarreras.ts` with TanStack Query hooks (list, create, update, delete)
- [x] 2.4 Build `CarreraFormModal` component with React Hook Form + Zod validation
- [x] 2.5 Build `AdminCarrerasPage` component composing DataTable + FormModal
- [x] 2.6 Write tests for CarreraFormModal validations and service calls

## 3. admin-cohortes Module

- [x] 3.1 Create `features/admin-cohortes/types/cohorte.ts` with Cohorte interface and DTOs
- [x] 3.2 Create `features/admin-cohortes/services/cohortes.service.ts`
- [x] 3.3 Create `features/admin-cohortes/hooks/useCohortes.ts` with TanStack Query hooks
- [x] 3.4 Build `CohorteFormModal` with carrera selector (async load), date pickers, Zod validation
- [x] 3.5 Build `AdminCohortesPage` with FilterBar (carrera filter) + DataTable + FormModal
- [x] 3.6 Write tests

## 4. admin-materias Module

- [x] 4.1 Create `features/admin-materias/types/materia.ts`
- [x] 4.2 Create `features/admin-materias/services/materias.service.ts`
- [x] 4.3 Create `features/admin-materias/hooks/useMaterias.ts`
- [x] 4.4 Build `MateriaFormModal` with code uniqueness validation
- [x] 4.5 Build `AdminMateriasPage`
- [x] 4.6 Write tests

## 5. admin-usuarios Module

- [x] 5.1 Create `features/admin-usuarios/types/usuario.ts` with Usuario interface (PII fields marked sensitive), CreateUsuarioDTO, UpdateUsuarioDTO
- [x] 5.2 Create `features/admin-usuarios/services/usuarios.service.ts` — PII only sent in POST/PATCH, never expected in GET response
- [x] 5.3 Create `features/admin-usuarios/hooks/useUsuarios.ts`
- [x] 5.4 Build `UsuarioFormModal` — sensitive fields shown empty on edit with "dato cifrado" indicator
- [x] 5.5 Build `AdminUsuariosPage` with estado filter + DataTable
- [x] 5.6 Write tests (including PII-not-exposed assertion)

## 6. admin-auditoria-panel Module

- [x] 6.1 Create `features/admin-auditoria-panel/types/auditoria.ts` with metrics and log entry interfaces
- [x] 6.2 Create `features/admin-auditoria-panel/services/auditoria.service.ts`
- [x] 6.3 Create `features/admin-auditoria-panel/hooks/` with hooks: `useActionsPerDay()`, `useCommsStatus()`, `useInteractions()`, `useLastActions()`
- [x] 6.4 Build `ActionsPerDayChart` (Recharts LineChart component)
- [x] 6.5 Build `CommsStatusChart` (Recharts PieChart/BarChart component)
- [x] 6.6 Build `InteractionsTable` with usage metrics per docente/materia
- [x] 6.7 Build `LastActionsLog` with configurable limit (default 200)
- [x] 6.8 Build `AdminAuditoriaPanelPage` composing FilterBar + MetricsGrid + charts + log
- [x] 6.9 Write tests for service hooks and component rendering

## 7. admin-auditoria-log Module

- [x] 7.1 Create `features/admin-auditoria-log/types/audit-log.ts` with AuditLogEntry interface
- [x] 7.2 Create `features/admin-auditoria-log/services/audit-log.service.ts` with filter query params
- [x] 7.3 Create `features/admin-auditoria-log/hooks/useAuditLog.ts` with paginated query
- [x] 7.4 Build `AdminAuditoriaLogPage` with FilterBar (date range, materia, usuario) + paginated DataTable
- [x] 7.5 Write tests

## 8. Routing & Integration

- [x] 8.1 Define route config `admin/carreras`, `admin/cohortes`, `admin/materias`, `admin/usuarios`, `admin/auditoria`, `admin/auditoria/log` for C-21 shell router
- [x] 8.2 Define sidebar items for "Administración" section with icons and permission guards (`estructura:gestionar`, `usuarios:gestionar`, `auditoria:ver`)
- [x] 8.3 Verify all pages load within C-21 layout and respect permission guards
