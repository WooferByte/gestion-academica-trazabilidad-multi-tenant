## Why

El backend de activia-trace ya está completo y desplegado con todos los endpoints de gestión académica (calificaciones, umbrales, análisis, comunicaciones). Falta la interfaz frontal que permita a los docentes y coordinadores usar estas capacidades. Sin las páginas frontend, el backend es inaccesible para los usuarios finales. Este change cierra esa brecha construyendo todas las páginas del módulo Académico.

## What Changes

- Nuevas páginas frontend bajo `/academico/` para el módulo Académico-Docente
- Comisión Dashboard con selector cascada materia+cohorte y KPIs
- Importación de calificaciones, padrón y reportes de finalización (multi-step upload wizard)
- Configuración de umbral de aprobación por comisión
- Vista de alumnos atrasados con selección y comunicación
- Ranking descendente por actividades aprobadas
- Notas finales con selector de actividades
- Exportación de TPs sin corregir (descarga CSV)
- Comunicación a alumnos con preview obligatorio (RN-16), envío individual/masivo, tracking de estados y aprobación de lotes
- Monitores de seguimiento (Tutor/Profesor y Coordinación) con filtros y exportación CSV
- Protección por permisos (`calificaciones:importar`, `atrasados:ver`, `comunicacion:enviar`, `comunicacion:aprobar`, `padron:cargar`)

## Capabilities

### New Capabilities
- `frontend-comision`: Dashboard de comisión con selector materia+cohorte, KPIs y menú de acciones
- `frontend-importacion`: Wizard multi-step para importar calificaciones, padrón, finalización y vaciar materia
- `frontend-analisis`: Páginas de atrasados, ranking, notas finales, TPs sin corregir y monitores de seguimiento
- `frontend-comunicaciones`: Preview obligatorio, envío individual y masivo, tracking de estados, cancelación y aprobación de lotes

### Modified Capabilities

*(Ninguna — todas las capabilities son nuevas)*

## Impact

- **Frontend**: Nuevos módulos feature en `src/features/academico/` con subdirectorios `comision/`, `importacion/`, `analisis/`, `comunicaciones/`
- **Routing**: Nuevas rutas anidadas bajo el layout protegido existente
- **Menu service**: Agregar items de menú para las nuevas páginas (ya existe "Académico" con hijos parciales)
- **API Client**: Ya existe el cliente Axios; los nuevos endpoints usan los mismos interceptores
- **Permisos**: Ya están definidos en backend; el frontend filtra por `user.permissions`
