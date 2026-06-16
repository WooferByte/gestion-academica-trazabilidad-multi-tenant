import api from "@/api/client";
import type { AsignacionListResponse, AsignacionResponse, AsignacionCreate } from "@/api/types";

export function listarAsignaciones() {
  return api.get<AsignacionListResponse>("/asignaciones");
}

export function crearAsignacion(data: AsignacionCreate) {
  return api.post<AsignacionResponse>("/asignaciones", data);
}

export function actualizarAsignacion(id: string, data: Partial<AsignacionCreate>) {
  return api.patch<AsignacionResponse>(`/asignaciones/${id}`, data);
}

export function eliminarAsignacion(id: string) {
  return api.delete<{ detail: string }>(`/asignaciones/${id}`);
}
