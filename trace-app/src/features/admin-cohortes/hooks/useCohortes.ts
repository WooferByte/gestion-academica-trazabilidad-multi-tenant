import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getCohortes,
  createCohorte,
  updateCohorte,
  deleteCohorte,
} from "../services/cohortes.service";
import type { CreateCohorteDTO, UpdateCohorteDTO } from "../types/cohorte";

export function useCohortes(params?: {
  carrera_id?: string;
  activo?: boolean;
  search?: string;
}) {
  return useQuery({
    queryKey: ["admin-cohortes", params],
    queryFn: () =>
      getCohortes(params).then((r) =>
        r.data.items.map((item) => ({
          ...item,
          activo: item.estado === "Activa",
        })),
      ),
    staleTime: 60 * 1000,
  });
}

export function useCrearCohorte() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateCohorteDTO) => createCohorte(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-cohortes"] }),
  });
}

export function useActualizarCohorte() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateCohorteDTO }) =>
      updateCohorte(id, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-cohortes"] }),
  });
}

export function useEliminarCohorte() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCohorte(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-cohortes"] }),
  });
}
