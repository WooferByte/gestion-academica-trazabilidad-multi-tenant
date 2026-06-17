import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getCarreras,
  createCarrera,
  updateCarrera,
  deleteCarrera,
} from "../services/carreras.service";
import type { CreateCarreraDTO, UpdateCarreraDTO } from "../types/carrera";

export function useCarreras(params?: { activo?: boolean; search?: string }) {
  return useQuery({
    queryKey: ["admin-carreras", params],
    queryFn: () =>
      getCarreras(params).then((r) =>
        r.data.items.map((item) => ({
          ...item,
          activo: item.estado === "Activa",
        })),
      ),
    staleTime: 60 * 1000,
  });
}



export function useCrearCarrera() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateCarreraDTO) => createCarrera(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-carreras"] }),
  });
}

export function useActualizarCarrera() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateCarreraDTO }) =>
      updateCarrera(id, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-carreras"] }),
  });
}

export function useEliminarCarrera() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCarrera(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-carreras"] }),
  });
}
