import { useMutation, useQueryClient } from "@tanstack/react-query";
import { reservarTurno, cancelarReserva } from "@/api/endpoints/coloquios";
import type { ReservaCreate } from "@/api/types";

export function useReservarTurno() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ evaluacionId, data }: { evaluacionId: string; data: ReservaCreate }) =>
      reservarTurno(evaluacionId, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-convocatoria"] });
    },
  });
}

export function useCancelarReserva() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reservaId: string) => cancelarReserva(reservaId).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-convocatoria"] });
    },
  });
}
