import { useMutation, useQueryClient } from "@tanstack/react-query";
import { clonarEquipo } from "@/api/endpoints/equipos";
import type { ClonarEquipoRequest } from "@/api/types";

export function useClonarEquipo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ClonarEquipoRequest) =>
      clonarEquipo(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mis-equipos"] });
    },
  });
}
