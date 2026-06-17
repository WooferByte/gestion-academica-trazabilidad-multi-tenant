# Skill: Backend Contract Verification

> **Propósito**: Evitar los errores de integración frontend-backend que ocurrieron en C-24a (frontend admin). Esta skill documenta todas las lecciones aprendidas y establece un proceso obligatorio para cualquier implementación frontend que consuma APIs del backend.

## Trigger

Cargar esta skill **SIEMPRE** antes de implementar cualquier feature frontend que consuma APIs del backend, especialmente cuando:
- Se crean nuevos services/endpoints en el frontend
- Se definen types/interfaces para respuestas del backend  
- Se implementan formularios que envían datos al backend
- Se implementan CRUDs (crear, leer, actualizar, eliminar)

## Problemas Encontrados en C-24a

### 1. HTTP Methods Incorrectos
**Problema**: El frontend usaba `api.patch()` pero el backend tenía `@router.put()`.
**Consecuencia**: 405 Method Not Allowed.
**Regla**: Verificar el decorador exacto en el router del backend (`@router.get`, `@router.post`, `@router.put`, `@router.patch`, `@router.delete`) antes de implementar el service.

### 2. Nombres de Campos Distintos (Frontend vs Backend)
**Problema**: El frontend asumía nombres de campos que no coincidían con el backend:
- Frontend: `activo: boolean` → Backend: `estado: "Activa"|"Inactiva"`
- Frontend: `apellidos` → Backend: `apellido`
- Frontend: `vigencia_desde/vigencia_hasta` → Backend: `vig_desde/vig_hasta`
- Frontend: `registros_afectados`, `ip_origen`, `agente_usuario` → Backend: `filas_afectadas`, `ip`, `user_agent`
**Consecuencia**: Validación 422 (extra='forbid'), datos undefined en pantalla.
**Regla**: Leer el schema Pydantic del backend (`backend/app/schemas/*.py`) y copiar los nombres EXACTOS de los campos.

### 3. Response Formatos Incorrectos (Wrapper vs Array)
**Problema**: El frontend esperaba arrays planos pero el backend devolvía `{ items: [...], total: N }` (y viceversa).
- CRUD list (carreras, cohortes, materias, usuarios): Backend devuelve `{ items, total }` → Frontend esperaba `[...]`
- Auditoría log: Backend devuelve `[...]` (array plano) → Frontend esperaba `{ items, total }`
**Consecuencia**: `data.map is not a function` o `data.items is undefined`.
**Regla**: Verificar el `response_model` del endpoint backend. Si es `list[Tipo]`, devuelve array plano. Si es un schema con `items: list[Tipo]`, devuelve `{ items, total }`.

### 4. URLs de Endpoints Incorrectas
**Problema**: Frontend llamaba a URLs que no existen en el backend:
- Frontend: `/auditoria/panel/actions-per-day` → Backend: `/auditoria/acciones-por-dia`
- Frontend: `/auditoria/panel/comms-status` → Backend: `/auditoria/comunicaciones-por-docente`
- Frontend: `/auditoria/panel/interactions` → Backend: `/auditoria/interacciones-por-docente-materia`
- Frontend: `/auditoria/panel/last-actions` → Backend: `/auditoria/log`
**Consecuencia**: 404 Not Found (silencioso en producción, datos no cargados).
**Regla**: Copiar el `prefix` del router + la ruta exacta del decorador del backend.

### 5. Campos Requeridos Faltantes
**Problema**: El frontend no enviaba campos requeridos por el backend.
- `password` faltaba en `UsuarioCreate`
**Consecuencia**: 422 Validation Error.
**Regla**: Revisar los campos requeridos (sin default, sin `None`) en el schema Pydantic.

### 6. `extra='forbid'` en Schemas Pydantic
**Problema**: Todos los schemas Pydantic en activia-trace tienen `model_config = ConfigDict(extra='forbid')`. Cualquier campo extra en la request es rechazado con 422.
**Consecuencia**: Errores silenciosos de validación.
**Regla**: 
- Para CREATE: enviar SOLO los campos definidos en `*Create` schema
- Para UPDATE: enviar SOLO los campos definidos en `*Update` schema 
- Nunca enviar campos que el backend no espera (ej: `email` en `UsuarioUpdate`)

### 7. Catch Blocks Silenciosos
**Problema**: Los catch blocks en los formularios no mostraban errores:
```typescript
} catch {
  // error handled by query client
}
```
**Consecuencia**: El usuario nunca veía el error. Parecía que "no funcionaba" sin feedback.
**Regla**: Siempre mostrar errores con `showToast()`:
```typescript
} catch (err) {
  const msg = err instanceof Error ? err.message : "Error desconocido";
  showToast(msg, "error");
}
```

## Proceso Obligatorio para Implementar un Endpoint

### Paso 1: Leer el Backend
Antes de escribir CUALQUIER línea de frontend, leer los archivos relevantes del backend:

```bash
# 1. Encontrar el router
backend/app/api/v1/routers/<modulo>.py

# 2. Encontrar los schemas (request/response)
backend/app/schemas/<modulo>.py

# 3. Verificar el service (lógica de negocio)
backend/app/services/<modulo>_service.py
```

### Paso 2: Documentar el Contrato
Extraer de los archivos del backend:

```markdown
## Contrato: <endpoint>

### URL
`<Método> /api/v1/<ruta>`

### Request (Create)
Campos del schema `*Create`:
- `campo1: tipo` (requerido)
- `campo2: tipo | None` (opcional)

### Request (Update)
Campos del schema `*Update`:
- Todos opcionales (`None`)

### Response (List)
Formato: `array` plano o `{ items, total }`
Campos del schema `*Response`:
- `campo1: tipo`
- `campo2: tipo`

### Response (Single)
Campos del schema `*Response`:
- Mismos que list pero sin wrapper
```

### Paso 3: Implementar en Orden
Siempre en este orden, verificando cada paso contra el contrato:

1. **Types** → cada campo EXACTAMENTE como en `*Response`
2. **Service** → URL exacta + método HTTP exacto + tipo de response exacto
3. **Hook** → mapear si es necesario (ej: `estado` → `activo`)
4. **MSW Handler** → mock data con los campos correctos
5. **Componente** → usar los nombres de campo del type
6. **Test** → testear contra el MSW handler

### Paso 4: Mapeo de Campos (si es necesario)
Cuando el frontend necesita names de dominio diferentes al backend, mapear en el hook:

```typescript
// Hook mapea backend → frontend
queryFn: () => getCarreras().then(r => 
  r.data.items.map(item => ({
    ...item,
    activo: item.estado === "Activa",  // backend estado → frontend activo
  }))
),

// Para mutations, mapear frontend → backend
mutationFn: (data) => createCarrera({
  ...data,
  estado: data.activo ? "Activa" : "Inactiva",
}),
```

## Lista de Verificación Pre-Implementación

- [ ] Leí el schema `*Create` del backend (sé qué campos envía POST)
- [ ] Leí el schema `*Update` del backend (sé qué campos envía PUT/PATCH)
- [ ] Leí el schema `*Response` del backend (sé qué campos recibo)
- [ ] Verifiqué el método HTTP exacto (GET/POST/PUT/PATCH/DELETE)
- [ ] Verifiqué la URL exacta (prefix + decorador)
- [ ] Verifiqué si la response es array plano o `{ items, total }`
- [ ] Verifiqué que `extra='forbid'` no va a rechazar mis campos
- [ ] Verifiqué que no falten campos requeridos (sin default en Pydantic)
- [ ] Agregué `showToast` en los catch blocks
- [ ] Probé contra el backend real (no solo MSW)
