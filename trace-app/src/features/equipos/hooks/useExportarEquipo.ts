import { useCallback, useState } from "react";
import { exportarEquipo } from "@/api/endpoints/equipos";

interface ExportParams {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
}

export function useExportarEquipo() {
  const [isExporting, setIsExporting] = useState(false);

  const download = useCallback(async (params: ExportParams) => {
    setIsExporting(true);
    try {
      const res = await exportarEquipo(params);
      const blob = new Blob([res.data], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "equipo-docente.csv";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
  }, []);

  return { download, isExporting };
}
