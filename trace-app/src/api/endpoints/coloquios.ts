import api from "@/api/client";
import type {
  EvaluacionCreate,
  EvaluacionListResponse,
  EvaluacionResponse,
  MetricasColoquiosResponse,
  ReservaCreate,
  ReservaResponse,
  ResultadoCreate,
  ResultadoResponse,
  ResultadosListResponse,
} from "@/api/types";

export function obtenerMetricas() {
  return api.get<MetricasColoquiosResponse>("/coloquios/metricas");
}

export function crearConvocatoria(data: EvaluacionCreate) {
  return api.post<EvaluacionResponse>("/coloquios/", data);
}

export function listarConvocatorias(params?: {
  materia_id?: string;
  cohorte_id?: string;
  tipo?: string;
  estado?: string;
  offset?: number;
  limit?: number;
}) {
  return api.get<EvaluacionListResponse>("/coloquios/", { params });
}

export function obtenerConvocatoria(evaluacionId: string) {
  return api.get<EvaluacionResponse>(`/coloquios/${evaluacionId}`);
}

export function importarAlumnos(evaluacionId: string, data: { alumno_ids: string[] }) {
  return api.post(`/coloquios/${evaluacionId}/alumnos`, data);
}

export function reservarTurno(evaluacionId: string, data: ReservaCreate) {
  return api.post<ReservaResponse>(`/coloquios/${evaluacionId}/reservas`, data);
}

export function cancelarReserva(reservaId: string) {
  return api.delete<{ id: string; estado: string; mensaje: string }>(`/coloquios/reservas/${reservaId}`);
}

export function registrarResultado(evaluacionId: string, alumnoId: string, data: ResultadoCreate) {
  return api.put<ResultadoResponse>(`/coloquios/${evaluacionId}/resultados/${alumnoId}`, data);
}

export function listarResultados(evaluacionId: string) {
  return api.get<ResultadosListResponse>(`/coloquios/${evaluacionId}/resultados`);
}

export function cerrarConvocatoria(evaluacionId: string) {
  return api.patch<EvaluacionResponse>(`/coloquios/${evaluacionId}/cerrar`);
}
