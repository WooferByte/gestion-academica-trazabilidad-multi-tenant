import api from "@/api/client";
import type {
  AckResponse,
  AvisoCreate,
  AvisoListResponse,
  AvisoResponse,
  AvisoUpdate,
} from "@/api/types";

export function crearAviso(data: AvisoCreate) {
  return api.post<AvisoResponse>("/avisos", data);
}

export function listarAvisos() {
  return api.get<AvisoListResponse>("/avisos");
}

export function obtenerAviso(avisoId: string) {
  return api.get<AvisoResponse>(`/avisos/${avisoId}`);
}

export function actualizarAviso(avisoId: string, data: AvisoUpdate) {
  return api.patch<AvisoResponse>(`/avisos/${avisoId}`, data);
}

export function eliminarAviso(avisoId: string) {
  return api.delete<{ detail: string }>(`/avisos/${avisoId}`);
}

export function confirmarLectura(avisoId: string) {
  return api.post<AckResponse>(`/avisos/${avisoId}/ack`);
}
