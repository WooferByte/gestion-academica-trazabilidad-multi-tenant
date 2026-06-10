import { useMutation } from "@tanstack/react-query";
import { enviarComunicacion } from "@/api/endpoints/comunicaciones";

export function useEnviarComunicacion() {
  return useMutation({
    mutationFn: (data: { destinatario: string; asunto: string; cuerpo: string }) =>
      enviarComunicacion(data).then((r) => r.data),
  });
}
