import { useMutation } from "@tanstack/react-query";
import { previewComunicacion } from "@/api/endpoints/comunicaciones";

export function useComunicacionPreview() {
  return useMutation({
    mutationFn: (data: { destinatario: string; asunto: string; cuerpo: string }) =>
      previewComunicacion(data).then((r) => r.data),
  });
}
