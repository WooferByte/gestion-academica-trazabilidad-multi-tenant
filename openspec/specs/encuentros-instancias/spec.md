## Requirements

### Requirement: Editar instancia de encuentro (F6.3)
El sistema SHALL exponer `PATCH /api/v1/encuentros/instancias/{id}` para actualizar una instancia existente. Solo accesible con permiso `encuentros:gestionar`. Campos editables: `estado` (Programado|Realizado|Cancelado), `meet_url`, `video_url`, `comentario`. Las instancias SHALL pertenecer al tenant del usuario autenticado (filtro por tenant_id).

#### Scenario: Cambiar estado a Realizado
- **WHEN** se actualiza una instancia con `estado=Realizado`
- **THEN** el sistema SHALL persistir el cambio y retornar la instancia actualizada

#### Scenario: Editar video_url después de realizado
- **WHEN** se actualiza una instancia con `video_url=https://vimeo.com/123`
- **THEN** el sistema SHALL guardar el enlace de grabación

#### Scenario: Cancelar un encuentro
- **WHEN** se actualiza una instancia con `estado=Cancelado`
- **THEN** el sistema SHALL cambiar el estado y mantener el resto de los datos

#### Scenario: Instancia inexistente retorna 404
- **WHEN** se intenta editar una instancia con ID inexistente
- **THEN** el sistema SHALL retornar 404

### Requirement: Generar bloque HTML para aula virtual (F6.4)
El sistema SHALL exponer `GET /api/v1/encuentros/instancias?materia_id=X&html=true` que retorna un fragmento HTML formateado con los encuentros de una materia, ordenados por fecha ascendente. Incluye: fecha, hora, título, estado y meet_url. El HTML SHALL ser auto-contenido (sin CSS externo).

#### Scenario: Generar HTML con encuentros programados
- **WHEN** se solicita HTML para una materia con 3 instancias programadas
- **THEN** el sistema SHALL retornar HTML con una tabla que incluye fecha, hora, título y enlace de cada instancia

#### Scenario: Materia sin encuentros retorna mensaje informativo
- **WHEN** se solicita HTML para una materia sin instancias
- **THEN** el sistema SHALL retornar `<p>No hay encuentros programados.</p>`
