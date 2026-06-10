import api from "@/api/client";
import type {
  ComunicacionPreviewResponse,
  ComunicacionResponse,
  ComunicacionesTrackingResponse,
} from "@/api/types";

export function previewComunicacion(data: {
  destinatario: string;
  asunto: string;
  cuerpo: string;
  variables?: Record<string, string>;
}) {
  return api.post<ComunicacionPreviewResponse>("/comunicaciones/preview", data);
}

export function enviarComunicacion(data: {
  destinatario: string;
  asunto: string;
  cuerpo: string;
  materia_id?: string;
  programada_para?: string;
}) {
  return api.post<ComunicacionResponse>("/comunicaciones", data);
}

export function enviarLote(data: {
  destinatarios: string[];
  asunto: string;
  cuerpo: string;
  materia_id?: string;
  programada_para?: string;
}) {
  return api.post<ComunicacionResponse[]>("/comunicaciones/lote", data);
}

export function aprobarLote(data: { lote_id: string }) {
  return api.post<{ detail: string }>("/comunicaciones/aprobar-lote", data);
}

export function cancelarComunicacion(id: string) {
  return api.post<{ detail: string }>(`/comunicaciones/${id}/cancelar`);
}

export function getComunicacionesTracking(params: { lote_id: string }) {
  return api.get<ComunicacionesTrackingResponse>("/comunicaciones", { params });
}
