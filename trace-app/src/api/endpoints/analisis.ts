import api from "@/api/client";
import type {
  AtrasadosResponse,
  RankingResponse,
  NotasFinalesResponse,
  TpsSinCorregirResponse,
  ReportesRapidosResponse,
  MonitorSeguimientoResponse,
  MonitorGeneralResponse,
} from "@/api/types";

export function getAtrasados(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<AtrasadosResponse>("/analisis/atrasados", { params });
}

export function getRanking(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<RankingResponse>("/analisis/ranking", { params });
}

export function getNotasFinales(params: {
  materia_id: string;
  cohorte_id: string;
  actividades: string;
}) {
  return api.get<NotasFinalesResponse>("/analisis/notas-finales", { params });
}

export function getTpsSinCorregir(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<TpsSinCorregirResponse>("/analisis/tps-sin-corregir", { params });
}

export function getActividades(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<{ items: Array<{ nombre: string; id: string }>; total: number }>(
    "/analisis/actividades", { params },
  );
}

export function getReportesRapidos(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<ReportesRapidosResponse>("/analisis/reportes-rapidos", { params });
}

export function getMonitorSeguimiento(params?: {
  materia_id?: string;
  comision?: string;
  busqueda?: string;
  desde?: string;
  hasta?: string;
  min_actividades?: number;
}) {
  return api.get<MonitorSeguimientoResponse>("/analisis/monitor-seguimiento", { params });
}

export function getMonitorGeneral(params?: {
  materia_id?: string;
  comision?: string;
  regional?: string;
  busqueda?: string;
}) {
  return api.get<MonitorGeneralResponse>("/analisis/monitor-general", { params });
}
