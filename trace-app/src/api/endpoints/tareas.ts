import api from "@/api/client";
import type {
  ComentarioCreate,
  ComentarioResponse,
  TareaCreate,
  TareaEstadoUpdate,
  TareaListResponse,
  TareaResponse,
  TareaUpdate,
} from "@/api/types";

export function listarMisTareas(params?: { materia_id?: string; estado?: string }) {
  return api.get<TareaListResponse>("/tareas/mis-tareas", { params });
}

export function crearTarea(data: TareaCreate) {
  return api.post<TareaResponse>("/tareas", data);
}

export function obtenerTarea(tareaId: string) {
  return api.get<TareaResponse>(`/tareas/${tareaId}`);
}

export function actualizarTarea(tareaId: string, data: TareaUpdate) {
  return api.patch<TareaResponse>(`/tareas/${tareaId}`, data);
}

export function cambiarEstado(tareaId: string, data: TareaEstadoUpdate) {
  return api.patch<TareaResponse>(`/tareas/${tareaId}/estado`, data);
}

export function eliminarTarea(tareaId: string) {
  return api.delete<TareaResponse>(`/tareas/${tareaId}`);
}

export function agregarComentario(tareaId: string, data: ComentarioCreate) {
  return api.post<ComentarioResponse>(`/tareas/${tareaId}/comentarios`, data);
}

export function listarTodasLasTareas(params?: {
  materia_id?: string;
  estado?: string;
  asignado_a?: string;
  asignado_por?: string;
  search?: string;
}) {
  return api.get<TareaListResponse>("/admin/tareas", { params });
}
