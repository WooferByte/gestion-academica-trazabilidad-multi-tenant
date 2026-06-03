## ADDED Requirements

### Requirement: Configurar umbral de aprobación por materia
The system SHALL allow PROFESOR to set the minimum passing percentage for their assigned materia×cohorte.

#### Scenario: Configurar umbral personalizado
- **WHEN** PROFESOR sets umbral_pct to 70 for materia X
- **THEN** the UmbralMateria record is created with umbral_pct=70 linked to the PROFESOR's asignacion

#### Scenario: Umbral por defecto (RN-03)
- **WHEN** no UmbralMateria exists for a materia×asignacion
- **THEN** the default umbral_pct of 60 is used for computing `aprobado`

#### Scenario: Actualizar umbral existente
- **WHEN** PROFESOR updates umbral_pct from 60 to 75
- **THEN** the existing UmbralMateria record is updated and the change is audited

#### Scenario: Umbral afecta derivación de aprobado
- **WHEN** Calificacion has nota_numerica=65 and umbral_pct is 70
- **THEN** `aprobado` is computed as `false`
- **WHEN** umbral_pct is later changed to 60
- **THEN** the same Calificacion now computes `aprobado` as `true`

### Requirement: Configurar valores textuales aprobatorios
The system SHALL allow configuring which textual values count as approved per materia.

#### Scenario: Valores textuales custom
- **WHEN** PROFESOR sets valores_aprobatorios to ["Aprobado", "Muy bueno"]
- **THEN** Calificaciones with those textual values compute `aprobado` as `true`
