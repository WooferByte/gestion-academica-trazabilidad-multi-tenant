import { useMutation, useQueryClient } from "@tanstack/react-query";
import { importarAlumnos } from "@/api/endpoints/coloquios";

export function useImportarAlumnos() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ evaluacionId, alumnoIds }: { evaluacionId: string; alumnoIds: string[] }) =>
      importarAlumnos(evaluacionId, { alumno_ids: alumnoIds }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-convocatoria"] });
    },
  });
}
