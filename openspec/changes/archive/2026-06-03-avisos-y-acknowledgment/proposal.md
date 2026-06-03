## Why

Activia-trace no tiene un canal de comunicación interno (tipo tablón de avisos) para que coordinadores y administradores publiquen información urgente u operativa visible por roles, cohortes o materias. Hoy cualquier comunicación institucional requiere emails o mensajes fuera del sistema, sin trazabilidad de lectura. Implementar el tablón de avisos permite comunicación segmentada con confirmación de lectura obligatoria (acuse), esencial para comunicar cambios de fechas, normas, alertas de atraso y otra información crítica en el contexto académico.

## What Changes

- Nuevos modelos `Aviso` (segmentable por alcance Global/PorMateria/PorCohorte/PorRol, severidad, vigencia, orden, requiere_ack) y `AcknowledgmentAviso` (confirmación de lectura)
- ABM completo de avisos con permiso `avisos:publicar` (COORDINADOR/ADMIN)
- Visualización de avisos para destinatarios según su rol/cohorte/materia (RN-18/19/20)
- Confirmación de lectura por ALUMNO/cualquier rol; contadores derivados de `AcknowledgmentAviso` (no desnormalizados)
- API REST `/api/v1/avisos/*`
- Migración Alembic 012 con tablas `aviso` y `acknowledgment_aviso`
- Cobertura de tests: filtrado por scope (rol/cohorte/materia), ventana de vigencia, acuse, orden por prioridad

## Capabilities

### New Capabilities
- `avisos-core`: Publicación, visualización segmentada y acuse de lectura de avisos del sistema con alcances (Global/PorMateria/PorCohorte/PorRol), severidad, ventana de vigencia y orden de prioridad

### Modified Capabilities

Ninguna. Capacidad nueva sin cambios sobre especificaciones existentes.

## Impact

- **Backend**: modelos `Aviso` y `AcknowledgmentAviso`, repositorio, servicio, schemas Pydantic, router con CRUD + visualización + confirmación
- **DB**: migración 012 con tablas `aviso` y `acknowledgment_aviso` e índices
- **Auth**: nuevo permiso `avisos:publicar` en la matriz RBAC
- **Frontend (futuro)**: no se toca ahora, pero la API expone todo necesario para el tablón
