import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listarSlots, obtenerSlot, crearSlot } from "@/api/endpoints/encuentros";
import type { SlotEncuentroCreate } from "@/api/types";

export function useSlotsList(materia_id?: string) {
  return useQuery({
    queryKey: ["encuentros-slots", materia_id],
    queryFn: async () => {
      const res = await listarSlots(materia_id);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useSlot(slotId: string) {
  return useQuery({
    queryKey: ["encuentros-slot", slotId],
    queryFn: async () => {
      const res = await obtenerSlot(slotId);
      return res.data;
    },
    enabled: !!slotId,
  });
}

export function useCrearSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SlotEncuentroCreate) => crearSlot(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["encuentros-slots"] });
    },
  });
}
