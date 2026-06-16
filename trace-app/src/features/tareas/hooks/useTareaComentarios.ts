import { useMutation, useQueryClient } from "@tanstack/react-query";
import { agregarComentario } from "@/api/endpoints/tareas";
import type { ComentarioCreate } from "@/api/types";

export function useAgregarComentario(tareaId: string | undefined) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComentarioCreate) =>
      agregarComentario(tareaId!, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tareas", tareaId] });
    },
  });
}
