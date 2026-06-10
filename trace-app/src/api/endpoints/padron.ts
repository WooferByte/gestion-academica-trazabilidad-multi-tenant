import api from "@/api/client";
import type {
  PadronPreviewResponse,
  PadronConfirmarResponse,
} from "@/api/types";

export function padronImportarPreview(formData: FormData) {
  return api.post<PadronPreviewResponse>("/padron/importar/preview", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function padronImportarConfirmar(formData: FormData) {
  return api.post<PadronConfirmarResponse>("/padron/importar/confirmar", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function vaciarMateria(materiaId: string, cohorteId: string) {
  return api.post<{ detail: string }>(
    `/padron/vaciar/${materiaId}/${cohorteId}`,
  );
}
