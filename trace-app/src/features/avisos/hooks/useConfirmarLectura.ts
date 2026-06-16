import { useMutation, useQueryClient } from "@tanstack/react-query";
import { confirmarLectura } from "@/api/endpoints/avisos";

export function useConfirmarLectura() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (avisoId: string) => confirmarLectura(avisoId).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avisos-activos"] });
      queryClient.invalidateQueries({ queryKey: ["avisos"] });
    },
  });
}
