import { useMutation } from "@tanstack/react-query";
import { vaciarMateria } from "@/api/endpoints/padron";

export function useVaciarMateria() {
  return useMutation({
    mutationFn: ({ materiaId, cohorteId }: { materiaId: string; cohorteId: string }) =>
      vaciarMateria(materiaId, cohorteId).then((r) => r.data),
  });
}
