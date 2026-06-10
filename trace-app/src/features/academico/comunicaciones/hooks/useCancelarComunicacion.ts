import { useMutation, useQueryClient } from "@tanstack/react-query";
import { cancelarComunicacion } from "@/api/endpoints/comunicaciones";

export function useCancelarComunicacion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => cancelarComunicacion(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comunicaciones-tracking"] });
    },
  });
}
