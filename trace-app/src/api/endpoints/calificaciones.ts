import api from "@/api/client";
import type {
  CalificacionesPreviewResponse,
  CalificacionesConfirmarResponse,
  Calificacion,
} from "@/api/types";

export function importarPreview(formData: FormData) {
  return api.post<CalificacionesPreviewResponse>("/calificaciones/importar/preview", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function importarConfirmar(formData: FormData) {
  return api.post<CalificacionesConfirmarResponse>("/calificaciones/importar/confirmar", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function importarFinalizacion(formData: FormData) {
  return api.post<{ materia_id: string; cohorte_id: string; total: number }>(
    "/calificaciones/importar/finalizacion",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
}

export function listarCalificaciones(params: {
  materia_id: string;
  cohorte_id: string;
}) {
  return api.get<Calificacion[]>("/calificaciones", { params });
}
