## ADDED Requirements

### Requirement: Crear slot recurrente (F6.1)
El sistema SHALL exponer `POST /api/v1/encuentros/slots` para crear un slot de encuentro recurrente. Solo accesible con permiso `encuentros:gestionar`. El slot SHALL contener: `asignacion_id`, `materia_id`, `titulo`, `hora`, `dia_semana`, `fecha_inicio`, `cant_semanas`, `meet_url`. El sistema SHALL generar automáticamente N instancias de `InstanciaEncuentro` según `cant_semanas`, con fechas sucesivas respetando `dia_semana` y `hora`. Cada instancia SHALL crearse con estado `Programado`.

#### Scenario: Slot recurrente semanal genera instancias
- **WHEN** se crea un slot con `fecha_inicio=2026-03-02`, `dia_semana=Lunes`, `hora=18:00`, `cant_semanas=4`
- **THEN** el sistema SHALL crear 4 instancias con fechas 2026-03-02, 2026-03-09, 2026-03-16, 2026-03-23, todas a las 18:00, estado Programado

#### Scenario: Slot con cant_semanas=0 no genera instancias
- **WHEN** se crea un slot con `cant_semanas=0`
- **THEN** el sistema SHALL crear el slot pero NO generar ninguna instancia automáticamente

#### Scenario: Validación de dia_semana inválido
- **WHEN** se envía `dia_semana=INVALIDO`
- **THEN** el sistema SHALL retornar 422 con error de validación

### Requirement: Crear encuentro único (F6.2)
El sistema SHALL exponer `POST /api/v1/encuentros/instancias` para crear una instancia de encuentro independiente (sin slot padre). Solo accesible con permiso `encuentros:gestionar`. Requiere: `materia_id`, `fecha`, `hora`, `titulo`, `meet_url` (opcional). El `slot_id` SHALL quedar nulo.

#### Scenario: Crear encuentro único exitoso
- **WHEN** se crea una instancia con `materia_id=X`, `fecha=2026-04-15`, `hora=10:00`, `titulo=Clase consulta`
- **THEN** el sistema SHALL crear la instancia con `slot_id=null`, estado Programado
