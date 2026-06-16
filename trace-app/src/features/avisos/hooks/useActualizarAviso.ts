import { useMutation, useQueryClient } from "@tanstack/react-query";
import { actualizarAviso } from "@/api/endpoints/avisos";
import type { AvisoUpdate } from "@/api/types";

export function useActualizarAviso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AvisoUpdate }) =>
      actualizarAviso(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avisos"] });
    },
  });
}
