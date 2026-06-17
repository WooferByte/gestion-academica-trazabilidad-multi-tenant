## ADDED Requirements

### Requirement: Panel de interacciones del sistema
El sistema SHALL proveer un dashboard visual para que usuarios con permiso `auditoria:ver` supervisen la actividad del tenant, consumiendo la API de C-19.

#### Scenario: Dashboard muestra acciones por día
- **WHEN** un ADMIN o COORDINADOR navega a `/admin/auditoria`
- **THEN** el sistema SHALL mostrar un gráfico de líneas (Recharts) con acciones registradas por día
- **AND** el gráfico SHALL tener tooltip con el detalle al hacer hover

#### Scenario: Dashboard muestra distribución de comunicaciones
- **WHEN** visualizando el panel
- **THEN** el sistema SHALL mostrar un gráfico de torta o barras agrupado por docente con la distribución de estados (Pendiente / Enviando / OK / Fallido / Cancelado)

#### Scenario: Dashboard muestra interacciones por docente y materia
- **WHEN** visualizando el panel
- **THEN** el sistema SHALL mostrar una tabla con métricas de uso por docente y materia: cantidad de análisis, vistas previas, importaciones, envíos, limpiezas, configuraciones de umbral

#### Scenario: Dashboard muestra últimas acciones
- **WHEN** visualizando el panel
- **THEN** el sistema SHALL mostrar una tabla con las últimas 200 acciones registradas (por defecto), con columnas: fecha/hora, usuario, acción, IP, user agent

#### Scenario: Filtros del dashboard
- **WHEN** un ADMIN aplica filtros (rango de fechas, materia, usuario, estado de actividad)
- **THEN** el sistema SHALL recargar todos los componentes del dashboard con los datos filtrados
- **AND** SHALL enviar los filtros como query params a la API

#### Scenario: Configurar límite de registros en últimas acciones
- **WHEN** un ADMIN modifica el límite de registros del log de últimas acciones
- **THEN** el sistema SHALL recargar la tabla con la nueva cantidad (máximo configurable, default 200)
