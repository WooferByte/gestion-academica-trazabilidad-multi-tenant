import { useMutation, useQueryClient } from "@tanstack/react-query";
import { aprobarLote } from "@/api/endpoints/comunicaciones";

export function useAprobarLote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (loteId: string) => aprobarLote({ lote_id: loteId }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comunicaciones-pendientes"] });
    },
  });
}
