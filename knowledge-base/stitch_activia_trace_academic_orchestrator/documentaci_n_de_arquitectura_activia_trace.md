# Arquitectura Frontend: activia-trace

## 1. Estructura de Proyecto (Feature-based)
Siguiendo el patrón de módulos por dominio para escalabilidad y desacoplamiento.

```text
src/
├── api/                # Cliente Axios centralizado + Interceptors
├── assets/             # Estáticos (imágenes, fuentes)
├── components/         # UI Components transversales (Shadcn/UI style)
│   ├── ui/             # Componentes base (Button, Input, Table, etc.)
│   ├── feedback/       # Modales, Toasts, Skeletons
│   └── forms/          # Controlled wrappers para React Hook Form
├── config/             # Constantes, env vars, RBAC mapping
├── features/           # Módulos core (C-21 a C-24)
│   ├── auth/           # Login, 2FA, Session management
│   ├── shell/          # App Layout, Sidebar, Breadcrumbs
│   ├── academico/      # Calificaciones, Atrasos, Coloquios
│   ├── coordinacion/   # Equipos docentes, Tablón, Monitor
│   ├── finanzas/       # Liquidaciones, Facturas, Grilla salarial
│   └── admin/          # Auditoría, Usuarios, Estructura
├── hooks/              # Custom hooks globales (useDebounce, useLocalStorage)
├── providers/          # QueryClient, Theme, Auth, Router providers
├── services/           # Tipos globales y lógica de negocio compartida
├── types/              # Definiciones TypeScript globales
└── utils/              # Helpers puros (date formatting, calc)
```

## 2. Estrategia de Navegación y RBAC
El acceso se gestiona mediante un componente `ProtectedRoute` que valida el token y los permisos `modulo:accion`.

| Ruta | Módulo | Acceso (Roles) |
| :--- | :--- | :--- |
| `/login` | Auth | Público |
| `/dashboard` | Shell | Todos (Vista adaptada) |
| `/academico/calificaciones` | Académico | PROFESOR, COORDINADOR, NEXO, ADMIN |
| `/academico/comunicaciones` | Académico | PROFESOR, COORDINADOR, NEXO, ADMIN |
| `/academico/coloquios` | Académico | ALUMNO, PROFESOR, COORDINADOR |
| `/coordinacion/monitor` | Coordinación | COORDINADOR, NEXO, ADMIN |
| `/coordinacion/equipos` | Coordinación | COORDINADOR, ADMIN |
| `/finanzas/liquidaciones` | Finanzas | FINANZAS, ADMIN |
| `/admin/auditoria` | Admin | ADMIN |

## 3. Estrategia de Estado
- **Server State (TanStack Query):** Toda la data de Moodle y base propia se cachea aquí. Cache invalidation mediante `onSuccess` en mutaciones.
- **URL State:** Filtros del Monitor y Tablón persisten en Query Params (`?materia=ID&estado=atrasado`) para permitir compartir links y navegación consistente.
- **Form State:** React Hook Form + Zod para validación en el cliente.
- **Global UI State:** Minimalista (ej. estado del sidebar) vía Zustand o Context API.

## 4. Decisiones Clave de Arquitectura
- **Multi-tenancy:** El ID del tenant se extrae del JWT tras el login. No se incluye en la URL para evitar ataques de navegación entre tenants. El cliente Axios lo inyecta automáticamente en los headers de cada request.
- **Impersonación:** El ADMIN puede generar un token de sesión "on-behalf-of". El Shell mostrará un banner persistente (ej. "Actuando como: [Usuario]") con opción de revertir.
- **Vigencia Temporal:** Los componentes de asignación masiva incluyen un DateRangePicker obligatorio. El backend filtra por `Date.now()`, pero el frontend permite visualizar históricos mediante un switch de "Ver finalizados".
- **Comunicaciones con Aprobación:** Workflow de 2 pasos. El PROFESOR redacta -> El mensaje entra en estado `PENDING_APPROVAL` -> El COORDINADOR aprueba desde su bandeja de entrada.
