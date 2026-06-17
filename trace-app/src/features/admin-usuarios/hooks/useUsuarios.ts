import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getUsuarios,
  createUsuario,
  updateUsuario,
  deleteUsuario,
} from "../services/usuarios.service";
import type { CreateUsuarioDTO, UpdateUsuarioDTO } from "../types/usuario";

export function useUsuarios(params?: {
  activo?: boolean;
  search?: string;
  rol?: string;
}) {
  return useQuery({
    queryKey: ["admin-usuarios", params],
    queryFn: () =>
      getUsuarios(params).then((r) =>
        r.data.items.map((item) => ({
          ...item,
          activo: item.estado === "Activo" || item.is_active === true,
          apellido: item.apellido ?? "",
        })),
      ),
    staleTime: 60 * 1000,
  });
}

export function useCrearUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateUsuarioDTO) =>
      createUsuario({
        ...data,
        apellido: (data as Record<string, unknown>).apellidos ?? data.apellido,
      } as CreateUsuarioDTO).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-usuarios"] }),
  });
}

export function useActualizarUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUsuarioDTO }) =>
      updateUsuario(id, {
        ...data,
        apellido: (data as Record<string, unknown>).apellidos ?? data.apellido,
      } as UpdateUsuarioDTO).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-usuarios"] }),
  });
}

export function useEliminarUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteUsuario(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-usuarios"] }),
  });
}
