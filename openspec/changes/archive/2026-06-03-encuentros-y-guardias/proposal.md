## Why

Los docentes necesitan planificar y registrar los encuentros sincrónicos (clases virtuales) sin depender de herramientas externas. Actualmente no hay trazabilidad de qué encuentros se programaron, cuáles se realizaron, ni dónde están las grabaciones. Tampoco existe un registro formal de las guardias de atención que los tutores cubren, dificultando la supervisión de coordinación y la liquidación de horas. Este change agrega ambos módulos para cerrar el flujo de gestión del equipo docente.

## What Changes

- Nuevos modelos `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con migración 010
- CRUD de slots recurrentes (generación automática de N instancias según `cant_semanas`) y encuentros únicos
- Edición de instancias: estado (Programado/Realizado/Cancelado), meet_url, video_url, comentario
- Endpoints REST para generación de bloque HTML listo para publicar en el aula virtual (F6.4)
- Vista transversal de encuentros para COORDINADOR/ADMIN (F6.5)
- Registro de guardias por TUTOR con consulta global + export para COORDINADOR/ADMIN (F6.6)
- Permiso `encuentros:gestionar` como guard en todos los endpoints
- Tests de generación de instancias recurrentes, encuentro único, edición de estado, registro de guardia, export

## Capabilities

### New Capabilities
- `encuentros-slots`: Creación de slots recurrentes y encuentros únicos, con generación automática de instancias según cant_semanas (F6.1, F6.2, RN-13)
- `encuentros-instancias`: Edición de instancias de encuentro (estado, meet_url, video_url, comentario), generación de bloque HTML (F6.3, F6.4)
- `encuentros-vista-global`: Vista transversal de todos los encuentros del tenant para coordinación/admin (F6.5)
- `guardias-registro`: Registro de guardias por tutor, consulta global y exportación para coordinación (F6.6)

### Modified Capabilities
- *(ninguna — no existen specs previas de encuentros o guardias)*

## Impact

- **Modelos nuevos**: `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` en SQLAlchemy
- **Migración nueva**: `010_encuentros_guardias.py`
- **Routers nuevos**: `/api/v1/encuentros/slots`, `/api/v1/encuentros/instancias`, `/api/v1/guardias`
- **Servicios nuevos**: `SlotEncuentroService`, `InstanciaEncuentroService`, `GuardiaService`
- **Repositories nuevos**: `SlotEncuentroRepository`, `InstanciaEncuentroRepository`, `GuardiaRepository`
- **Permiso nuevo**: `encuentros:gestionar` en el catálogo de permisos
- **Tests**: tests de integración con DB real para cada funcionalidad
- **Dependencias**: requiere C-07 (usuarios + asignaciones) — asume tablas `asignacion` y `usuario` existentes
