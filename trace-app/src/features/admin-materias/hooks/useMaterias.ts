import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getMaterias,
  createMateria,
  updateMateria,
  deleteMateria,
} from "../services/materias.service";
import type { CreateMateriaDTO, UpdateMateriaDTO } from "../types/materia";

export function useMaterias(params?: { activo?: boolean; search?: string }) {
  return useQuery({
    queryKey: ["admin-materias", params],
    queryFn: () =>
      getMaterias(params).then((r) =>
        r.data.items.map((item) => ({
          ...item,
          activo: item.estado === "Activa",
        })),
      ),
    staleTime: 60 * 1000,
  });
}

export function useCrearMateria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateMateriaDTO) => createMateria(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-materias"] }),
  });
}

export function useActualizarMateria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateMateriaDTO }) =>
      updateMateria(id, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-materias"] }),
  });
}

export function useEliminarMateria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteMateria(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-materias"] }),
  });
}
