import { useMutation } from "@tanstack/react-query";
import { enviarLote } from "@/api/endpoints/comunicaciones";

export function useEnviarLote() {
  return useMutation({
    mutationFn: (data: { destinatarios: string[]; asunto: string; cuerpo: string }) =>
      enviarLote(data).then((r) => r.data),
  });
}
