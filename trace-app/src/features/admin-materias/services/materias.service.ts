import api from "@/api/client";
import type { Materia, CreateMateriaDTO, UpdateMateriaDTO } from "../types/materia";

export function getMaterias(params?: { activo?: boolean }) {
  return api.get<{ items: Materia[]; total: number }>("/admin/materias", { params });
}

export function getMateria(id: string) {
  return api.get<Materia>(`/admin/materias/${id}`);
}

export function createMateria(data: CreateMateriaDTO) {
  return api.post<Materia>("/admin/materias", data);
}

export function updateMateria(id: string, data: UpdateMateriaDTO) {
  return api.put<Materia>(`/admin/materias/${id}`, data);
}

export function deleteMateria(id: string) {
  return api.delete<void>(`/admin/materias/${id}`);
}
