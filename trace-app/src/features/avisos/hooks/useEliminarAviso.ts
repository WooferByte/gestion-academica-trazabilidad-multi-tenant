import { useMutation, useQueryClient } from "@tanstack/react-query";
import { eliminarAviso } from "@/api/endpoints/avisos";

export function useEliminarAviso() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => eliminarAviso(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avisos"] });
    },
  });
}
