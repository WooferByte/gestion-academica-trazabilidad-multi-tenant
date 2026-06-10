import { useMutation } from "@tanstack/react-query";
import { padronImportarPreview, padronImportarConfirmar } from "@/api/endpoints/padron";

export function usePadronPreview() {
  return useMutation({
    mutationFn: (formData: FormData) => padronImportarPreview(formData).then((r) => r.data),
  });
}

export function usePadronConfirmar() {
  return useMutation({
    mutationFn: (formData: FormData) => padronImportarConfirmar(formData).then((r) => r.data),
  });
}
