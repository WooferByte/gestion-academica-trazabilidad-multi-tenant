## ADDED Requirements

### Requirement: Crear versión de padrón

El sistema SHALL permitir crear una nueva versión de padrón para una materia×cohorte determinada. Al activar una versión, la versión activa anterior de esa misma materia×cohorte SHALL desactivarse automáticamente. Las versiones inactivas se conservan para histórico.

#### Scenario: Activar versión desactiva la anterior
- **WHEN** se crea y activa una nueva versión de padrón para (materia X, cohorte Y)
- **THEN** la versión previamente activa para (materia X, cohorte Y) pasa a `activa = False`
- **AND** solo existe una versión con `activa = True` para ese par (materia X, cohorte Y)

#### Scenario: Aislamiento entre pares materia×cohorte
- **WHEN** se activa una nueva versión para (materia A, cohorte 1)
- **THEN** la versión activa de (materia A, cohorte 2) NO se ve afectada
- **AND** la versión activa de (materia B, cohorte 1) NO se ve afectada

### Requirement: Importar padrón desde archivo xlsx/csv

El sistema SHALL aceptar archivos `.xlsx` (openpyxl) y `.csv` con columnas: `nombre`, `apellidos`, `email`, `comision`, `regional`. El sistema SHALL generar una vista previa de los datos detectados antes de confirmar la importación. Al confirmar, SHALL crear una nueva versión con todas las entradas.

#### Scenario: Vista previa de import xlsx
- **WHEN** el usuario sube un archivo `.xlsx` válido con 10 filas de datos
- **THEN** el sistema retorna una vista previa con las 10 filas sin persistir en DB

#### Scenario: Confirmar import persiste versión y entradas
- **WHEN** el usuario confirma la vista previa de un archivo con 3 alumnos
- **THEN** se crea una nueva `VersionPadron` con `activa = True`
- **AND** se crean 3 registros `EntradaPadron` vinculados a esa versión

#### Scenario: Entrada sin usuario_id (alumno sin cuenta)
- **WHEN** se importa un alumno cuyo email no existe en `users`
- **THEN** la `EntradaPadron` se crea con `usuario_id = NULL`
- **AND** se almacenan `nombre`, `apellidos` y `email` desnormalizados

#### Scenario: Archivo con formato inválido
- **WHEN** el usuario sube un archivo que no es `.xlsx` ni `.csv`
- **THEN** el sistema retorna error 400 con mensaje descriptivo

#### Scenario: Aislamiento tenant en import
- **WHEN** el tenant A importa un padrón para materia M
- **THEN** los datos del tenant B no se ven afectados
- **AND** el tenant B no puede acceder a las entradas del tenant A

### Requirement: Vaciar datos de padrón de una materia

El sistema SHALL permitir vaciar (soft delete) todas las entradas de padrón y desactivar la versión activa de una materia, respetando el scope `(usuario_id × materia_id)` de RN-04. SHALL registrar un evento de auditoría `PADRON_CARGAR`.

#### Scenario: Vaciar materia desactiva versión
- **WHEN** el usuario ejecuta vaciar datos sobre materia M
- **THEN** la versión activa de materia M se marca como `activa = False` (no se borra)
- **AND** todas las `EntradaPadron` de esa versión reciben `deleted_at` con timestamp

#### Scenario: Vaciar no afecta otras materias
- **WHEN** el usuario ejecuta vaciar datos sobre materia A
- **THEN** los datos de padrón de materia B permanecen intactos

### Requirement: Auditoría de PADRON_CARGAR

El sistema SHALL registrar un evento de auditoría con código `PADRON_CARGAR` cada vez que se importa un padrón o se vacían datos de una materia.

#### Scenario: Audit tras import
- **WHEN** se confirma una importación de padrón con 5 entradas
- **THEN** se registra `AuditLog` con código `PADRON_CARGAR`, cantidad = 5, materia_id, usuario_id, tenant_id

#### Scenario: Audit tras vaciar
- **WHEN** se ejecuta vaciar datos de materia M con 12 entradas afectadas
- **THEN** se registra `AuditLog` con código `PADRON_CARGAR`, cantidad = 12, materia_id, usuario_id, tenant_id
