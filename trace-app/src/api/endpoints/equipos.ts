import api from "@/api/client";
import type {
  AsignacionListResponse,
  AsignacionMasivaRequest,
  AsignacionResponse,
  ClonarEquipoRequest,
  VigenciaEquipoRequest,
  VigenciaUpdateResponse,
} from "@/api/types";

export function getMisEquipos(params?: {
  materia_id?: string;
  cohorte_id?: string;
  solo_vigentes?: boolean;
}) {
  return api.get<AsignacionListResponse>("/equipos/mis-equipos", { params });
}

export function asignacionMasiva(data: AsignacionMasivaRequest) {
  return api.post<AsignacionResponse[]>("/equipos/asignacion-masiva", data);
}

export function clonarEquipo(data: ClonarEquipoRequest) {
  return api.post<AsignacionResponse[]>("/equipos/clonar", data);
}

export function modificarVigencia(data: VigenciaEquipoRequest) {
  return api.patch<VigenciaUpdateResponse>("/equipos/vigencia", data);
}

export function exportarEquipo(params: {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
}) {
  return api.get<Blob>("/equipos/exportar", {
    params,
    responseType: "blob",
  });
}
