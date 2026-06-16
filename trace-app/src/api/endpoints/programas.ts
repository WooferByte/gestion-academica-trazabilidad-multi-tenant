import api from "@/api/client";
import type {
  ProgramaMateriaCreate,
  ProgramaMateriaResponse,
  ProgramaMateriaUpdate,
} from "@/api/types";

export function listProgramas() {
  return api.get<{ items: ProgramaMateriaResponse[]; total: number }>("/admin/programas");
}

export function createPrograma(data: ProgramaMateriaCreate) {
  return api.post<ProgramaMateriaResponse>("/admin/programas", data);
}

export function getPrograma(programaId: string) {
  return api.get<ProgramaMateriaResponse>(`/admin/programas/${programaId}`);
}

export function updatePrograma(programaId: string, data: ProgramaMateriaUpdate) {
  return api.put<ProgramaMateriaResponse>(`/admin/programas/${programaId}`, data);
}

export function deletePrograma(programaId: string) {
  return api.delete(`/admin/programas/${programaId}`);
}
