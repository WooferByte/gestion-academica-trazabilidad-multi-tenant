export interface EquipoFilters {
  materia_id?: string;
  cohorte_id?: string;
  solo_vigentes?: boolean;
}

export interface AsignacionMasivaForm {
  usuario_ids: string[];
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  rol: string;
  comisiones?: string[];
  responsable_id?: string;
  desde?: string;
  hasta?: string;
}

export interface ClonarEquipoForm {
  origen: {
    materia_id: string;
    carrera_id: string;
    cohorte_id: string;
  };
  destino: {
    materia_id: string;
    carrera_id: string;
    cohorte_id: string;
    desde?: string;
    hasta?: string;
  };
}

export interface VigenciaForm {
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  desde?: string;
  hasta?: string;
}
