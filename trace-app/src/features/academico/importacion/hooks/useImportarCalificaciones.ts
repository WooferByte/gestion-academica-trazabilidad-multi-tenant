import { useMutation } from "@tanstack/react-query";
import { importarPreview, importarConfirmar, importarFinalizacion } from "@/api/endpoints/calificaciones";

export function useImportarPreview() {
  return useMutation({
    mutationFn: (formData: FormData) => importarPreview(formData).then((r) => r.data),
  });
}

export function useImportarConfirmar() {
  return useMutation({
    mutationFn: (formData: FormData) => importarConfirmar(formData).then((r) => r.data),
  });
}

export function useImportarFinalizacion() {
  return useMutation({
    mutationFn: (formData: FormData) => importarFinalizacion(formData).then((r) => r.data),
  });
}
