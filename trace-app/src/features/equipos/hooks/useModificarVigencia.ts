import { useMutation, useQueryClient } from "@tanstack/react-query";
import { modificarVigencia } from "@/api/endpoints/equipos";
import type { VigenciaEquipoRequest } from "@/api/types";

export function useModificarVigencia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: VigenciaEquipoRequest) =>
      modificarVigencia(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mis-equipos"] });
    },
  });
}
