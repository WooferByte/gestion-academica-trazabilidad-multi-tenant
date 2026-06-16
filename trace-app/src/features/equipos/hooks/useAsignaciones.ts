import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listarAsignaciones, crearAsignacion, actualizarAsignacion, eliminarAsignacion } from "@/api/endpoints/asignaciones";

export function useAsignaciones() {
  return useQuery({
    queryKey: ["asignaciones"],
    queryFn: () => listarAsignaciones().then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useCrearAsignacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: import("@/api/types").AsignacionCreate) => crearAsignacion(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asignaciones"] }),
  });
}

export function useActualizarAsignacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<import("@/api/types").AsignacionCreate> }) => actualizarAsignacion(id, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asignaciones"] }),
  });
}

export function useEliminarAsignacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => eliminarAsignacion(id).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asignaciones"] }),
  });
}
