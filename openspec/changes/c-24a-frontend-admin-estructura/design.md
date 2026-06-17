## Context

activia-trace provee las APIs backend para administración de estructura académica (C-06: carreras, cohortes, materias), usuarios del tenant (C-07) y auditoría (C-19). Sin embargo, no existe interfaz frontend que consuma estos endpoints. El shell de C-21 (login, sidebar, layout, API client) proporciona la base sobre la cual montar los módulos administrativos.

Este change implementa 6 feature modules frontend que cubren las secciones de administración del tenant. El estado actual del proyecto indica que no hay frontend construido aún (dependencia C-21 no implementada), por lo que el diseño asume las convenciones del proyecto pero no requiere integración con código existente.

## Goals / Non-Goals

**Goals:**
- 6 feature modules administrables desde el sidebar del shell (C-21)
- CRUD completo con paginación, filtros, formularios y confirmación de eliminación
- Panel de auditoría con gráficos de actividad y log detallado
- Feature-based module pattern (components, hooks, services, types, pages)
- TanStack Query para server state, React Hook Form + Zod para formularios

**Non-Goals:**
- No tocar backend (endpoints ya existen en C-06, C-07, C-19)
- No implementar el shell/layout (C-21)
- No implementar autenticación ni guard de rutas (C-21)
- No implementar diseño responsive mobile (sigue el patrón del shell)
- No incluir tests E2E (solo unit tests con Vitest)

## Decisions

### D1 — Feature module structure
- **Qué**: Cada módulo sigue `features/{name}/{components,hooks,services,types,pages}/`
- **Por qué**: Consistente con la arquitectura feature-based definida en el stack del proyecto. Cada módulo es autónomo y se puede desarrollar en paralelo.
- **Alternativa**: Monolithic pages/ — descartada por no escalar con 6 módulos.

### D2 — Shared components pattern
- **Qué**: Se crea `features/admin-estructura/shared/` con componentes reutilizables entre los ABM: `DataTable`, `SearchInput`, `StatusBadge`, `ConfirmDialog`, `EmptyState`, `PageHeader`, `FilterBar`.
- **Por qué**: Los 4 ABM (carreras, cohortes, materias, usuarios) comparten el mismo patrón CRUD. Centralizar reduce duplicación y asegura consistencia visual.
- **Alternativa**: Copiar el patrón en cada módulo — descartado por violar DRY.

### D3 — TanStack Query con hooks tipados
- **Qué**: Cada módulo expone hooks `useCarreras()`, `useCrearCarrera()` etc. en `hooks/` que envuelven TanStack Query.
- **Por qué**: TanStack Query es el estándar del proyecto para server state. Los hooks encapsulan la lógica de fetch/cache/mutación.
- **Alternativa**: useState + useEffect directo — descartado por falta de cache, refetch y loading states.

### D4 — React Router layout anidado
- **Qué**: Las rutas se definen como `admin/carreras`, `admin/cohortes`, `admin/materias`, `admin/usuarios`, `admin/auditoria`. Se agregan al sidebar del shell en sección "Administración".
- **Por qué**: Sigue la convención de C-21 para sidebar items con icono + label, filtrados por permisos del usuario.

### D5 — PII nunca al frontend
- **Qué**: Los formularios de usuario envían campos PII pero nunca los reciben de vuelta en GET (según spec user-management). El formulario de edición solo muestra placeholders/indicadores de presencia.
- **Por qué**: Cumple con el requisito de seguridad de C-07 de no exponer PII en texto plano.

### D6 — Recharts para gráficos de auditoría
- **Qué**: El panel de auditoría usa Recharts para el gráfico de acciones-por-día y la distribución de estados de comunicación.
- **Por qué**: Librería liviana, React-native, bien tipada con TypeScript.
- **Alternativa**: Chart.js + react-chartjs-2 — descartado por peor integración con React y tipado más débil.

### D7 — Filtros server-side en log de auditoría
- **Qué**: El log completo usa filtros que se envían como query params a la API, no filtrado client-side.
- **Por qué**: El volumen de registros de auditoría puede ser muy grande (>200 registros por consulta). Filtrar client-side sería ineficiente.
- **Alternativa**: Filtrado client-side — descartado por performance.

## Routes Design

| Path | Module | Descripción |
|------|--------|-------------|
| `/admin/carreras` | admin-carreras | Lista paginada + ABM carreras |
| `/admin/cohortes` | admin-cohortes | Lista paginada + ABM cohortes |
| `/admin/materias` | admin-materias | Lista paginada + ABM materias |
| `/admin/usuarios` | admin-usuarios | Lista paginada + ABM usuarios |
| `/admin/auditoria` | admin-auditoria-panel | Dashboard de interacciones |
| `/admin/auditoria/log` | admin-auditoria-log | Log completo con filtros |

## Component Tree (por módulo)

### admin-carreras
```
AdminCarrerasPage
├── PageHeader (title + "Nueva Carrera" button)
├── DataTable
│   ├── Columns: Código, Nombre, Estado (Badge), Acciones
│   └── Actions: Editar, Activar/Inactivar, Eliminar
└── CarreraFormModal (Dialog con React Hook Form + Zod)
    ├── Input: código (text, required, unique)
    ├── Input: nombre (text, required)
    └── Estado: toggle activo/inactivo
```

### admin-cohortes
```
AdminCohortesPage
├── PageHeader
├── FilterBar (filtro por carrera)
├── DataTable
│   ├── Columns: Nombre, Carrera, Año, Vigencia, Estado, Acciones
│   └── Actions: Editar, Eliminar
└── CohorteFormModal
    ├── Select: carrera (carga async)
    ├── Input: nombre (text, required)
    ├── Input: año (number)
    ├── DatePicker: vigencia desde
    ├── DatePicker: vigencia hasta
    └── Estado: toggle
```

### admin-materias
```
AdminMateriasPage
├── PageHeader
├── DataTable
│   ├── Columns: Código, Nombre, Estado, Acciones
│   └── Actions: Editar, Activar/Inactivar, Eliminar
└── MateriaFormModal
    ├── Input: código (text, required, unique)
    ├── Input: nombre (text, required)
    └── Estado: toggle
```

### admin-usuarios
```
AdminUsuariosPage
├── PageHeader
├── FilterBar (filtro por estado)
├── DataTable
│   ├── Columns: Nombre, Email, Legajo, Rol, Estado, Acciones
│   └── Actions: Editar, Desactivar
└── UsuarioFormModal
    ├── Input: nombre
    ├── Input: apellidos
    ├── Input: email
    ├── Input: dni
    ├── Input: cuil
    ├── Input: banco
    ├── Input: cbu (PII)
    ├── Input: alias_cbu (PII)
    ├── Input: regional
    ├── Input: legajo
    ├── Select: facturador (sí/no)
    └── Estado: toggle activo/inactivo
```

### admin-auditoria-panel
```
AdminAuditoriaPanelPage
├── PageHeader
├── FilterBar (fecha desde, fecha hasta, materia, usuario, estado)
├── MetricsGrid
│   ├── ActionsPerDayChart (Recharts LineChart)
│   ├── CommsStatusChart (Recharts PieChart por docente)
│   └── InteractionsTable (por docente y materia)
└── LastActionsLog (tabla con máx 200 registros)
```

### admin-auditoria-log
```
AdminAuditoriaLogPage
├── PageHeader
├── FilterBar (fecha desde, fecha hasta, materia, usuario)
├── DataTable
│   ├── Columns: Fecha/Hora, Usuario, Materia, Acción, Registros, IP, User Agent
│   └── Paginación server-side
└── EmptyState cuando sin resultados
```

## Data Flow

```
[React Page] → TanStack Query Hook → Service (Axios) → API Backend
                                                         ↓
[React Page] ← Cache/Data ← Query Response ← Controller
```

Para mutaciones:
```
[Form Modal] → React Hook Form + Zod (validación client-side)
  → useMutation Hook → Service (Axios POST/PUT/DELETE)
  → queryClient.invalidateQueries() (refetch lista)
  → Toast de éxito/error
```

## Risks / Trade-offs

- **[Riesgo] Frontend sin C-21 implementado**: Los módulos no se pueden integrar hasta que el shell exista. La navegación y los guards de ruta dependen de C-21.
  - **Mitigación**: Cada módulo se implementa como una página independiente que se monta en la ruta. La integración con C-21 es solo agregar la ruta al router y el item al sidebar.

- **[Riesgo] APIs backend no disponibles**: C-06, C-07, C-19 pueden no estar implementados aún.
  - **Mitigación**: Los services de API se diseñan contra el contrato de los specs existentes. Se pueden probar con mocks mientras tanto.

- **[Trade-off] Shared components en admin-estructura vs shared global**: Los componentes compartidos se crean dentro del módulo `admin-estructura/shared/` en lugar de `shared/components/` para mantener el módulo autocontenido. Si otros módulos necesitan estos componentes, se migran a shared global en un change posterior.
