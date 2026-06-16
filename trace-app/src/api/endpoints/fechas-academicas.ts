import api from "@/api/client";
import type {
  FechaAcademicaCreate,
  FechaAcademicaResponse,
  FechaAcademicaUpdate,
} from "@/api/types";

export function listFechas(params?: {
  materia_id?: string;
  cohorte_id?: string;
  tipo?: string;
  periodo?: string;
}) {
  return api.get<{ items: FechaAcademicaResponse[]; total: number }>("/admin/fechas-academicas", { params });
}

export function createFecha(data: FechaAcademicaCreate) {
  return api.post<FechaAcademicaResponse>("/admin/fechas-academicas", data);
}

export function getFecha(fechaId: string) {
  return api.get<FechaAcademicaResponse>(`/admin/fechas-academicas/${fechaId}`);
}

export function updateFecha(fechaId: string, data: FechaAcademicaUpdate) {
  return api.put<FechaAcademicaResponse>(`/admin/fechas-academicas/${fechaId}`, data);
}

export function deleteFecha(fechaId: string) {
  return api.delete(`/admin/fechas-academicas/${fechaId}`);
}
