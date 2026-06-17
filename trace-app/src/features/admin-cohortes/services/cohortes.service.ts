import api from "@/api/client";
import type { Cohorte, CreateCohorteDTO, UpdateCohorteDTO } from "../types/cohorte";

export function getCohortes(params?: {
  carrera_id?: string;
  activo?: boolean;
  search?: string;
}) {
  return api.get<{ items: Cohorte[]; total: number }>("/admin/cohortes", { params });
}

export function getCohorte(id: string) {
  return api.get<Cohorte>(`/admin/cohortes/${id}`);
}

export function createCohorte(data: CreateCohorteDTO) {
  return api.post<Cohorte>("/admin/cohortes", data);
}

export function updateCohorte(id: string, data: UpdateCohorteDTO) {
  return api.put<Cohorte>(`/admin/cohortes/${id}`, data);
}

export function deleteCohorte(id: string) {
  return api.delete<void>(`/admin/cohortes/${id}`);
}
