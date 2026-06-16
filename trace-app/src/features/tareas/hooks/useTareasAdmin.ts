import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listarTodasLasTareas,
  cambiarEstado,
} from "@/api/endpoints/tareas";
import type { TareaEstadoUpdate } from "@/api/types";

const ADMIN_TAREAS_KEY = ["tareas", "admin"];

export function useTodasLasTareas(filters?: {
  materia_id?: string;
  estado?: string;
  asignado_a?: string;
  asignado_por?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: [...ADMIN_TAREAS_KEY, filters],
    queryFn: async () => {
      const res = await listarTodasLasTareas(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useCambiarEstadoAdmin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TareaEstadoUpdate }) =>
      cambiarEstado(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tareas"] });
    },
  });
}
