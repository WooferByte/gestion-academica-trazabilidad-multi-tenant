import { useExportarGuardias } from "@/features/encuentros/hooks/useGuardias";
import { showToast } from "@/components/ui/Toast";

interface ExportCsvButtonProps {
  filters?: {
    materia_id?: string;
    carrera_id?: string;
    cohorte_id?: string;
    estado?: string;
  };
}

export function ExportCsvButton({ filters }: ExportCsvButtonProps) {
  const exportMutation = useExportarGuardias();

  const handleExport = async () => {
    try {
      const result = await exportMutation.mutateAsync(filters);
      const blob = result instanceof Blob ? result : new Blob([String(result)], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "guardias.csv";
      a.click();
      URL.revokeObjectURL(url);
      showToast("Exportación completada", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al exportar";
      showToast(msg, "error");
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={exportMutation.isPending}
      className="px-4 py-2 text-sm rounded-md border border-border hover:bg-surface-variant disabled:opacity-50 transition-colors"
    >
      {exportMutation.isPending ? "Exportando..." : "Exportar CSV"}
    </button>
  );
}
