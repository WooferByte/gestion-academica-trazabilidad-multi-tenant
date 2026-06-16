import api from "@/api/client";
import type {
  GuardiaCreate,
  GuardiaListResponse,
  GuardiaResponse,
  GuardiaUpdate,
} from "@/api/types";

export function registrarGuardia(data: GuardiaCreate) {
  return api.post<GuardiaResponse>("/guardias", data);
}

export function listarGuardias(params?: {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
  estado?: string;
  offset?: number;
  limit?: number;
}) {
  return api.get<GuardiaListResponse>("/guardias", { params });
}

export function actualizarGuardia(guardiaId: string, data: GuardiaUpdate) {
  return api.patch<GuardiaResponse>(`/guardias/${guardiaId}`, data);
}

export function exportarGuardiasCSV(params?: {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
  estado?: string;
}) {
  return api.get<string>("/guardias/export", {
    params,
    responseType: "blob",
  });
}
