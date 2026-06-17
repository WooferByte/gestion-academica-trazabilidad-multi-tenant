import api from "@/api/client";
import type { Usuario, CreateUsuarioDTO, UpdateUsuarioDTO } from "../types/usuario";

export function getUsuarios(params?: {
  activo?: boolean;
  search?: string;
  rol?: string;
}) {
  return api.get<{ items: Usuario[]; total: number }>("/admin/usuarios", { params });
}

export function getUsuario(id: string) {
  return api.get<Usuario>(`/admin/usuarios/${id}`);
}

export function createUsuario(data: CreateUsuarioDTO) {
  return api.post<Usuario>("/admin/usuarios", data);
}

export function updateUsuario(id: string, data: UpdateUsuarioDTO) {
  return api.patch<Usuario>(`/admin/usuarios/${id}`, data);
}

export function deleteUsuario(id: string) {
  return api.delete<void>(`/admin/usuarios/${id}`);
}
