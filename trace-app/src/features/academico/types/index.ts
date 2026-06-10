export interface Comision {
  id: string;
  materia_id: string;
  materia_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  rol: string;
}

export interface KPIReporte {
  total_alumnos: number;
  total_actividades: number;
  aprobados: number;
  atrasados: number;
  promedio_general: number;
}

export interface Actividad {
  id: string;
  nombre: string;
  tipo: string;
  fecha: string;
}

export interface AlumnoAtrasado {
  id: string;
  nombre: string;
  apellido: string;
  legajo: string;
  actividades_totales: number;
  actividades_aprobadas: number;
  estado: "faltantes" | "desaprobadas";
}

export interface RankingItem {
  id: string;
  nombre: string;
  apellido: string;
  legajo: string;
  actividades_aprobadas: number;
  actividades_totales: number;
  porcentaje: number;
}

export interface NotaAlumno {
  alumno_id: string;
  nombre: string;
  apellido: string;
  legajo: string;
  notas: Record<string, number | null>;
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

export interface ComunicacionTrackingItem {
  id: string;
  alumno_id: string;
  nombre: string;
  apellido: string;
  estado: "pendiente" | "enviando" | "enviado" | "error" | "cancelado";
  timestamp: string;
  error_mensaje?: string;
}

export type UploadState = "idle" | "uploading" | "preview" | "confirming" | "done" | "error";

export interface ImportPreviewData {
  file_token: string;
  filename: string;
  actividades: Actividad[];
  filas_preview: Record<string, unknown>[];
}

export interface CommSelection {
  materiaId: string;
  cohorteId: string;
  selectedAlumnos?: string[];
}
