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
  id: string;
  alumno_id: string;
  nombre: string;
  apellido: string;
  legajo: string;
  actividad_nombre: string;
  actividad_tipo: string;
  fecha_entrega: string;
}

export interface TpsSinCorregirResponse {
  tps: TpSinCorregir[];
}

export interface MonitorItem {
  alumno_id: string;
  nombre: string;
  apellido: string;
  legajo: string;
  materia: string;
  comision: string;
  actividades_aprobadas: number;
  actividades_totales: number;
  porcentaje: number;
  ultima_actividad: string;
}

export interface MonitorSeguimientoResponse {
  items: MonitorItem[];
}

export interface MonitorGeneralResponse {
  items: MonitorItem[];
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
