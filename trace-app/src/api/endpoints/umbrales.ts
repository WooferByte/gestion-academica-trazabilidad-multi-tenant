import api from "@/api/client";
import type { UmbralResponse } from "@/api/types";

export function getUmbral(materiaId: string, cohorteId: string) {
  return api.get<UmbralResponse>(`/umbrales/${materiaId}/${cohorteId}`);
}

export function updateUmbral(materiaId: string, cohorteId: string, data: { umbral_pct: number }) {
  return api.put<UmbralResponse>(`/umbrales/${materiaId}/${cohorteId}`, data);
}
