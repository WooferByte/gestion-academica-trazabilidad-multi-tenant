import api from "@/api/client";
import type { Carrera, CreateCarreraDTO, UpdateCarreraDTO } from "../types/carrera";

export function getCarreras(params?: { activo?: boolean; search?: string }) {
  return api.get<{ items: Carrera[]; total: number }>("/admin/carreras", { params });
}

export function getCarrera(id: string) {
  return api.get<Carrera>(`/admin/carreras/${id}`);
}

export function createCarrera(data: CreateCarreraDTO) {
  return api.post<Carrera>("/admin/carreras", data);
}

export function updateCarrera(id: string, data: UpdateCarreraDTO) {
  return api.put<Carrera>(`/admin/carreras/${id}`, data);
}

export function deleteCarrera(id: string) {
  return api.delete<void>(`/admin/carreras/${id}`);
}
