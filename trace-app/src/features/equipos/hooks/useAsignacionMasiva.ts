import { useMutation, useQueryClient } from "@tanstack/react-query";
import { asignacionMasiva } from "@/api/endpoints/equipos";
import type { AsignacionMasivaRequest } from "@/api/types";

export function useAsignacionMasiva() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AsignacionMasivaRequest) =>
      asignacionMasiva(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mis-equipos"] });
    },
  });
}
