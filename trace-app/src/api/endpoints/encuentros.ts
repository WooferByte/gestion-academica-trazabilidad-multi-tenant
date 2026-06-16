import api from "@/api/client";
import type {
  SlotEncuentroCreate,
  SlotEncuentroListResponse,
  SlotEncuentroResponse,
  InstanciaEncuentroCreate,
  InstanciaEncuentroListResponse,
  InstanciaEncuentroResponse,
  InstanciaEncuentroUpdate,
} from "@/api/types";

export function crearSlot(data: SlotEncuentroCreate) {
  return api.post<SlotEncuentroResponse>("/encuentros/slots", data);
}

export function listarSlots(materia_id?: string) {
  const params = materia_id ? { materia_id } : undefined;
  return api.get<SlotEncuentroListResponse>("/encuentros/slots", { params });
}

export function obtenerSlot(slotId: string) {
  return api.get<SlotEncuentroResponse>(`/encuentros/slots/${slotId}`);
}

export function crearInstancia(data: InstanciaEncuentroCreate) {
  return api.post<InstanciaEncuentroResponse>("/encuentros/instancias", data);
}

export function listarInstancias(params?: {
  materia_id?: string;
  desde?: string;
  hasta?: string;
  estado?: string;
  slot_id?: string;
  offset?: number;
  limit?: number;
}) {
  return api.get<InstanciaEncuentroListResponse>("/encuentros/instancias", { params });
}

export function editarInstancia(instanciaId: string, data: InstanciaEncuentroUpdate) {
  return api.patch<InstanciaEncuentroResponse>(`/encuentros/instancias/${instanciaId}`, data);
}

export function generarHtml(materiaId: string) {
  return api.get<string>(`/encuentros/instancias?html=true&materia_id=${materiaId}`, {
    responseType: "text",
  });
}
