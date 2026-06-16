export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  requires_2fa: boolean;
}

export interface Verify2faRequest {
  code: string;
  temp_token: string;
}

export interface Verify2faResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RecoveryRequest {
  email: string;
}

export interface RecoveryConfirmRequest {
  token: string;
  new_password: string;
}

export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  roles: string[];
  permisos: string[];
  tenant_id: string;
}

export interface ForgotResponse {
  detail: string;
  token?: string;
  expires_in?: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}

// --- Academic API Types ---

export interface Comision {
  id: string;
  materia_id: string;
  materia_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  rol: string;
}

export interface ReportesRapidosResponse {
  materia_id: string;
  cohorte_id: string;
  total_alumnos: number;
  total_actividades: number;
  alumnos_aprobados: number;
  alumnos_atrasados: number;
  promedio_general: number | null;
}

export interface UmbralResponse {
  materia_id: string;
  cohorte_id: string;
  umbral_pct: number;
}

export interface Actividad {
  id: string;
  nombre: string;
  tipo: string;
  fecha: string;
}

export interface AlumnoAtrasado {
  entrada_padron_id: string;
  nombre: string;
  apellidos: string;
  email: string;
  comision: string;
  regional: string;
  actividades_faltantes: string[];
  actividades_desaprobadas: string[];
  total_actividades: number;
  aprobadas: number;
}

export interface AtrasadosResponse {
  items: AlumnoAtrasado[];
  total: number;
}

export interface RankingItem {
  entrada_padron_id: string;
  nombre: string;
  apellidos: string;
  comision: string;
  actividades_aprobadas: number;
}

export interface RankingResponse {
  items: RankingItem[];
  total: number;
}

export interface NotaFinalAlumno {
  entrada_padron_id: string;
  nombre: string;
  apellidos: string;
  nota_final: number | null;
  actividades_consideradas: number;
}

export interface NotasFinalesResponse {
  items: NotaFinalAlumno[];
  total: number;
}

export interface TpSinCorregir {
  entrada_padron_id: string;
  nombre: string;
  apellido: string;
  actividad: string;
  comision: string;
}

export interface TpsSinCorregirResponse {
  items: TpSinCorregir[];
  total: number;
}

export interface MonitorSeguimientoItem {
  entrada_padron_id: string;
  nombre: string;
  apellidos: string;
  comision: string;
  materia_id: string;
  actividad: string;
  nota_numerica: number | null;
  nota_textual: string | null;
  aprobado: boolean | null;
  importado_at: string | null;
}

export interface MonitorGeneralItem {
  entrada_padron_id: string;
  nombre: string;
  apellidos: string;
  comision: string;
  regional: string;
  materia_id: string;
  materia_nombre: string;
  actividad: string;
  nota_numerica: number | null;
  nota_textual: string | null;
  aprobado: boolean | null;
  importado_at: string | null;
}

export interface MonitorSeguimientoResponse {
  items: MonitorSeguimientoItem[];
  total: number;
}

export interface MonitorGeneralResponse {
  items: MonitorGeneralItem[];
  total: number;
}

export interface CalificacionesPreviewResponse {
  file_token: string;
  filename: string;
  actividades: Actividad[];
  filas_preview: Record<string, unknown>[];
}

export interface CalificacionesConfirmarResponse {
  materia_id: string;
  cohorte_id: string;
  calificaciones_creadas: number;
  actividades_procesadas: string[];
}

export interface Calificacion {
  id: string;
  alumno_id: string;
  actividad_id: string;
  nota: number;
  fecha: string;
}

export interface PadronPreviewResponse {
  materia_id: string;
  cohorte_id: string;
  total: number;
  items: Array<{
    nombre: string;
    apellidos: string;
    email: string;
    comision: string;
    regional: string;
  }>;
}

export interface PadronConfirmarResponse {
  detail: string;
  importados: number;
}

export interface ComunicacionPreviewResponse {
  asunto_renderizado: string;
  cuerpo_renderizado: string;
  variables_no_encontradas: string[];
}

export interface ComunicacionResponse {
  id: string;
  tenant_id: string;
  enviado_por: string | null;
  materia_id: string | null;
  destinatario: string;
  asunto: string;
  cuerpo: string;
  estado: string;
  lote_id: string;
  aprobacion_requerida: boolean;
  error_msg: string | null;
  programada_para: string | null;
  enviada_at: string | null;
  aprobada_por: string | null;
  cancelada_por: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ComunicacionTrackingItem {
  id: string;
  alumno_id: string;
  nombre: string;
  apellido: string;
  estado: "pendiente" | "enviando" | "enviado" | "error" | "cancelado";
  timestamp: string;
  error_mensaje?: string;
}

export interface ComunicacionesTrackingResponse {
	items: ComunicacionTrackingItem[];
	lote_id: string;
	lote_estado: string;
}

// --- Equipos Docentes Types ---

export interface AsignacionResponse {
	id: string;
	tenant_id: string;
	usuario_id: string;
	usuario_nombre: string;
	rol: string;
	materia_id: string | null;
	materia_nombre: string | null;
	carrera_id: string | null;
	carrera_nombre: string | null;
	cohorte_id: string | null;
	cohorte_nombre: string | null;
	comisiones: string[] | null;
	responsable_id: string | null;
	desde: string | null;
	hasta: string | null;
	created_at: string;
	updated_at: string;
	deleted_at: string | null;
}

export interface AsignacionListResponse {
	items: AsignacionResponse[];
	total: number;
}

export interface AsignacionCreate {
  usuario_id: string;
  rol: string;
  materia_id?: string | null;
  carrera_id?: string | null;
  cohorte_id?: string | null;
  comisiones?: string[] | null;
  responsable_id?: string | null;
  desde?: string | null;
  hasta?: string | null;
}

export interface AsignacionMasivaRequest {
	usuario_ids: string[];
	materia_id?: string | null;
	carrera_id?: string | null;
	cohorte_id?: string | null;
	rol: string;
	comisiones?: string[] | null;
	responsable_id?: string | null;
	desde?: string | null;
	hasta?: string | null;
}

export interface ClonarEquipoRequest {
	origen: {
		materia_id?: string | null;
		carrera_id?: string | null;
		cohorte_id?: string | null;
	};
	destino: {
		materia_id?: string | null;
		carrera_id?: string | null;
		cohorte_id?: string | null;
		desde?: string | null;
		hasta?: string | null;
	};
}

export interface VigenciaEquipoRequest {
	materia_id: string;
	carrera_id: string;
	cohorte_id: string;
	desde?: string | null;
	hasta?: string | null;
}

export interface VigenciaUpdateResponse {
	filas_afectadas: number;
}

// --- Avisos Types ---

export interface AvisoResponse {
	id: string;
	tenant_id: string;
	alcance: string;
	materia_id: string | null;
	cohorte_id: string | null;
	rol_destino: string | null;
	severidad: string;
	titulo: string;
	cuerpo: string;
	inicio_vigencia: string;
	fin_vigencia: string;
	orden: number;
	activo: boolean;
	requiere_ack: boolean;
	total_acks: number;
	user_acked: boolean;
	created_at: string | null;
	updated_at: string | null;
}

export interface AvisoListResponse {
	items: AvisoResponse[];
	total: number;
}

export interface AvisoCreate {
	alcance: string;
	materia_id?: string | null;
	cohorte_id?: string | null;
	rol_destino?: string | null;
	severidad?: string;
	titulo: string;
	cuerpo: string;
	inicio_vigencia: string;
	fin_vigencia: string;
	orden?: number;
	requiere_ack?: boolean;
}

export interface AvisoUpdate {
	alcance?: string | null;
	materia_id?: string | null;
	cohorte_id?: string | null;
	rol_destino?: string | null;
	severidad?: string | null;
	titulo?: string | null;
	cuerpo?: string | null;
	inicio_vigencia?: string | null;
	fin_vigencia?: string | null;
	orden?: number | null;
	activo?: boolean | null;
	requiere_ack?: boolean | null;
}

export interface AckResponse {
	id: string;
	aviso_id: string;
	usuario_id: string;
	confirmado_at: string;
}

// --- Encuentros Types ---

export interface SlotEncuentroResponse {
	id: string;
	tenant_id: string;
	asignacion_id: string;
	materia_id: string;
	titulo: string;
	hora: string;
	dia_semana: string;
	fecha_inicio: string;
	cant_semanas: number;
	fecha_unica: string | null;
	meet_url: string | null;
	vig_desde: string | null;
	vig_hasta: string | null;
	created_at: string | null;
	updated_at: string | null;
}

export interface SlotEncuentroListResponse {
	items: SlotEncuentroResponse[];
	total: number;
}

export interface SlotEncuentroCreate {
	asignacion_id: string;
	materia_id: string;
	titulo: string;
	hora: string;
	dia_semana: string;
	fecha_inicio: string;
	cant_semanas?: number;
	fecha_unica?: string | null;
	meet_url?: string | null;
	vig_desde?: string | null;
	vig_hasta?: string | null;
}

export interface InstanciaEncuentroResponse {
	id: string;
	tenant_id: string;
	slot_id: string | null;
	materia_id: string;
	fecha: string;
	hora: string;
	titulo: string;
	estado: string;
	meet_url: string | null;
	video_url: string | null;
	comentario: string | null;
	created_at: string | null;
	updated_at: string | null;
}

export interface InstanciaEncuentroListResponse {
	items: InstanciaEncuentroResponse[];
	total: number;
}

export interface InstanciaEncuentroCreate {
	materia_id: string;
	fecha: string;
	hora: string;
	titulo: string;
	meet_url?: string | null;
}

export interface InstanciaEncuentroUpdate {
	estado?: string | null;
	meet_url?: string | null;
	video_url?: string | null;
	comentario?: string | null;
}

// --- Guardias Types ---

export interface GuardiaResponse {
	id: string;
	tenant_id: string;
	asignacion_id: string;
	materia_id: string;
	carrera_id: string | null;
	cohorte_id: string | null;
	dia: string;
	horario: string;
	estado: string;
	comentarios: string | null;
	created_at: string | null;
	updated_at: string | null;
}

export interface GuardiaListResponse {
	items: GuardiaResponse[];
	total: number;
}

export interface GuardiaCreate {
	asignacion_id: string;
	materia_id: string;
	carrera_id?: string | null;
	cohorte_id?: string | null;
	dia: string;
	horario: string;
	comentarios?: string | null;
}

export interface GuardiaUpdate {
	estado: string;
	comentarios?: string | null;
}

// --- Coloquios Types ---

export interface TurnoColoquioResponse {
	id: string;
	evaluacion_id: string;
	fecha: string;
	hora_inicio: string;
	hora_fin: string;
	cupo: number;
	ocupados: number;
	created_at: string | null;
	updated_at: string | null;
}

export interface EvaluacionResponse {
	id: string;
	tenant_id: string;
	materia_id: string;
	cohorte_id: string;
	tipo: string;
	instancia: string;
	estado: string;
	dias_disponibles: number;
	turnos: TurnoColoquioResponse[];
	total_convocados: number;
	reservas_activas: number;
	cupos_libres: number;
	created_at: string | null;
	updated_at: string | null;
}

export interface EvaluacionListResponse {
	items: EvaluacionResponse[];
	total: number;
}

export interface MetricasColoquiosResponse {
	total_convocatorias_activas: number;
	total_alumnos_convocados: number;
	total_reservas_activas: number;
	total_resultados_registrados: number;
}

export interface EvaluacionCreate {
	materia_id: string;
	cohorte_id: string;
	instancia: string;
	tipo: string;
	turnos: TurnoColoquioCreate[];
}

export interface TurnoColoquioCreate {
	fecha: string;
	hora_inicio: string;
	hora_fin: string;
	cupo: number;
}

export interface ReservaCreate {
	turno_id: string;
}

export interface ReservaResponse {
	id: string;
	turno_id: string;
	alumno_id: string;
	evaluacion_id: string;
	estado: string;
	created_at: string | null;
	updated_at: string | null;
}

export interface AlumnosImportRequest {
	alumno_ids: string[];
}

export interface ResultadoCreate {
	nota_final: string;
}

export interface ResultadoResponse {
	id: string;
	evaluacion_id: string;
	alumno_id: string;
	nota_final: string;
	created_at: string | null;
	updated_at: string | null;
}

export interface ResultadosListResponse {
	items: ResultadoResponse[];
	total: number;
}

// --- Tareas Types ---

export interface ComentarioResponse {
  id: string;
  tarea_id: string;
  autor_id: string;
  autor_nombre?: string;
  texto: string;
  creado_at: string;
}

export interface TareaResponse {
  id: string;
  tenant_id: string;
  materia_id: string | null;
  asignado_a: string;
  asignado_a_nombre?: string;
  asignado_por: string;
  asignado_por_nombre?: string;
  estado: string;
  descripcion: string;
  contexto_id: string | null;
  comentarios: ComentarioResponse[];
  created_at: string | null;
  updated_at: string | null;
}

export interface TareaListResponse {
  items: TareaResponse[];
  total: number;
}

export interface TareaCreate {
  materia_id?: string | null;
  asignado_a: string;
  descripcion: string;
  contexto_id?: string | null;
}

export interface TareaUpdate {
  descripcion?: string;
  asignado_a?: string;
}

export interface TareaEstadoUpdate {
  estado: string;
}

export interface ComentarioCreate {
  texto: string;
}

// --- Setup Types ---

export interface ProgramaMateriaResponse {
  id: string;
  tenant_id: string;
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  titulo: string;
  referencia_archivo: string | null;
  cargado_at: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface ProgramaMateriaCreate {
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  titulo: string;
  referencia_archivo?: string | null;
}

export interface ProgramaMateriaUpdate {
  titulo?: string;
  referencia_archivo?: string | null;
}

export interface FechaAcademicaResponse {
  id: string;
  tenant_id: string;
  materia_id: string;
  cohorte_id: string;
  tipo: string;
  numero: number;
  periodo: string;
  fecha: string;
  titulo: string;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface FechaAcademicaCreate {
  materia_id: string;
  cohorte_id: string;
  tipo: string;
  numero: number;
  periodo: string;
  fecha: string;
  titulo: string;
}

export interface FechaAcademicaUpdate {
  tipo?: string;
  numero?: number;
  periodo?: string;
  fecha?: string;
  titulo?: string;
}
