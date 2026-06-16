import { useMutation, useQueryClient } from "@tanstack/react-query";
import { crearAviso } from "@/api/endpoints/avisos";
import type { AvisoCreate } from "@/api/types";

export function useCrearAviso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AvisoCreate) => crearAviso(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avisos"] });
    },
  });
}
