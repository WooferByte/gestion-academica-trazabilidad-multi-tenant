import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listarInstancias, editarInstancia, generarHtml } from "@/api/endpoints/encuentros";
import type { InstanciaEncuentroUpdate } from "@/api/types";
import type { InstanciaFilters } from "@/features/encuentros/types";

export function useInstanciasList(filters: InstanciaFilters) {
  return useQuery({
    queryKey: ["encuentros-instancias", filters],
    queryFn: async () => {
      const res = await listarInstancias(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useEditarInstancia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: InstanciaEncuentroUpdate }) =>
      editarInstancia(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["encuentros-instancias"] });
    },
  });
}

export function useGenerarHtml() {
  return useMutation({
    mutationFn: (materiaId: string) => generarHtml(materiaId).then((r) => r.data),
  });
}
