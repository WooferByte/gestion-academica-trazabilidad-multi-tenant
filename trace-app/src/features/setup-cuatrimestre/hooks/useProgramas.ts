import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listProgramas,
  createPrograma,
  getPrograma,
  updatePrograma,
  deletePrograma,
} from "@/api/endpoints/programas";
import type {
  ProgramaMateriaCreate,
  ProgramaMateriaUpdate,
} from "@/api/types";

const PROGRAMAS_KEY = ["programas"];

export function useProgramasList() {
  return useQuery({
    queryKey: PROGRAMAS_KEY,
    queryFn: async () => {
      const res = await listProgramas();
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function usePrograma(programaId: string | undefined) {
  return useQuery({
    queryKey: [...PROGRAMAS_KEY, programaId],
    queryFn: async () => {
      const res = await getPrograma(programaId!);
      return res.data;
    },
    enabled: !!programaId,
  });
}

export function useCrearPrograma() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProgramaMateriaCreate) =>
      createPrograma(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROGRAMAS_KEY });
    },
  });
}

export function useActualizarPrograma() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProgramaMateriaUpdate }) =>
      updatePrograma(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROGRAMAS_KEY });
    },
  });
}

export function useEliminarPrograma() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deletePrograma(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROGRAMAS_KEY });
    },
  });
}
