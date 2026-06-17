## Why

Los módulos de administración del tenant (estructura académica, usuarios, auditoría) son el punto de entrada para configurar y operar cualquier tenant en activia-trace. Sin su frontend, el sistema no es usable por el perfil ADMIN ni COORDINADOR. Este change cierra esa brecha construyendo las 3 secciones administrativas que consumen los endpoints de C-06 (estructura), C-07 (usuarios) y C-19 (panel auditoría), todo sobre el shell de C-21.

## What Changes

### Nuevas capacidades

1. **ABM Carreras (F5.1)**: CRUD completo con tabla paginada, formulario de alta/edición, toggle activo/inactivo con validación de cohortes abiertas, soft delete.
2. **ABM Cohortes (F5.2)**: CRUD completo vinculado a carrera, tabla paginada con filtro por carrera, formulario que impide asignar a carrera inactiva.
3. **ABM Materias (F5.1)**: CRUD completo con unicidad de código, tabla paginada, formulario de alta/edición.
4. **ABM Usuarios del tenant (F4.1)**: CRUD con campos PII (sin exponer en texto plano), asignación de roles, filtro por estado, soft delete.
5. **Panel de Auditoría (F9.1)**: dashboard con gráfico acciones-por-día, distribución de estados de comunicaciones, interacciones por docente/materia, log de últimas acciones con filtros.
6. **Log Completo de Auditoría (F9.2)**: tabla paginada de auditoría con filtros (fechas, materia, usuario, estado), datos de IP y user agent.

### Sin modificaciones a capacidades existentes

No se modifican specs existentes. Se crean nuevos specs de frontend que consumen APIs ya especificadas.

## Capabilities

### New Capabilities
- `admin-carreras`: ABM carreras con validación de unicidad y estado activo/inactivo
- `admin-cohortes`: ABM cohortes vinculadas a carrera con vigencia temporal
- `admin-materias`: ABM materias con código único por tenant
- `admin-usuarios`: ABM usuarios del tenant con PII cifrada y asignación de roles
- `admin-auditoria-panel`: Dashboard de interacciones del sistema con gráficos y filtros
- `admin-auditoria-log`: Log completo de auditoría con filtros avanzados

### Modified Capabilities
_(Ninguna — no se modifican specs existentes)_

## Impact

- **Frontend**: 6 nuevos feature modules en `frontend/src/features/` (admin-carreras, admin-cohortes, admin-materias, admin-usuarios, admin-auditoria-panel, admin-auditoria-log)
- **Routing**: Nuevas rutas anidadas bajo `/admin/` en el sidebar del shell (C-21)
- **Dependencias**: Consume APIs de C-06 (estructura), C-07 (usuarios), C-19 (auditoría). Requiere C-21 (shell, auth guard, layout, sidebar, api client)
- **Sin cambios backend**: este change es frontend-only, no toca Python
