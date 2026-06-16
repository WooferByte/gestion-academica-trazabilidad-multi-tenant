import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listarMisTareas,
  crearTarea,
  obtenerTarea,
  actualizarTarea,
  cambiarEstado,
  eliminarTarea,
} from "@/api/endpoints/tareas";
import type { TareaCreate, TareaEstadoUpdate, TareaUpdate } from "@/api/types";

const TAREAS_KEY = ["tareas", "mis-tareas"];

export function useMisTareas(filters?: { materia_id?: string; estado?: string }) {
  return useQuery({
    queryKey: [...TAREAS_KEY, filters],
    queryFn: async () => {
      const res = await listarMisTareas(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useTarea(tareaId: string | undefined) {
  return useQuery({
    queryKey: ["tareas", tareaId],
    queryFn: async () => {
      const res = await obtenerTarea(tareaId!);
      return res.data;
    },
    enabled: !!tareaId,
  });
}

export function useCrearTarea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TareaCreate) => crearTarea(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TAREAS_KEY });
    },
  });
}

export function useActualizarTarea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TareaUpdate }) =>
      actualizarTarea(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tareas"] });
    },
  });
}

export function useCambiarEstado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TareaEstadoUpdate }) =>
      cambiarEstado(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tareas"] });
    },
  });
}

export function useEliminarTarea() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => eliminarTarea(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TAREAS_KEY });
    },
  });
}
