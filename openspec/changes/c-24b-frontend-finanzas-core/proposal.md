## Why

El módulo de Finanzas es necesario para que el rol FINANZAS y ADMIN puedan gestionar liquidaciones de honorarios, facturas de docentes facturantes y la grilla salarial (bases y plus). Sin este frontend, los endpoints del backend (C-18) no tienen interfaz de usuario. Este change implementa las 3 secciones del menú Finanzas: Liquidaciones, Facturas y Grilla Salarial.

## What Changes

- Nuevo feature module `features/finanzas-liquidaciones/` con Liquidaciones list/calcular/cerrar/historial/exportar
- Nuevo feature module `features/finanzas-facturas/` con Facturas list/crear/detalle/cambio-estado
- Nuevo feature module `features/finanzas-grilla/` con Grilla Salarial (Bases CRUD + Pluses CRUD)
- Nuevas rutas en RouterProvider bajo `/liquidaciones`, `/facturas`, `/finanzas/grilla`
- Nuevas entradas en menu.service.ts para la sección Finanzas
- Nuevos types/service/hooks/pages/components para cada módulo

No se modifican capabilities existentes. Se agregan 3 nuevas capabilities.

## Capabilities

### New Capabilities
- `finanzas-liquidaciones`: Gestión de liquidaciones de honorarios: listar, calcular, cerrar, historial, exportar CSV. Permisos: `liquidaciones:ver`, `liquidaciones:calcular`, `liquidaciones:cerrar`, `liquidaciones:exportar`.
- `finanzas-facturas`: Gestión de facturas de docentes facturantes: listar, crear, detalle, cambio de estado (pendiente/abonada). Permiso: `facturas:gestionar`.
- `finanzas-grilla-salarial`: Administración de grilla salarial: salarios base (CRUD) y salarios plus (CRUD con toggle y asignación masiva por categoría). Permiso: `liquidaciones:configurar-salarios`.

### Modified Capabilities
<!-- none -->

## Impact

- `trace-app/src/providers/RouterProvider.tsx` — nuevas rutas lazy-loaded
- `trace-app/src/features/shell/services/menu.service.ts` — nuevos items en sección Finanzas
- 3 nuevos feature modules bajo `trace-app/src/features/`
- Sin cambios en backend ni base de datos (frontend-only)
