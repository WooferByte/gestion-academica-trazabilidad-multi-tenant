import { useState } from "react";
import { generarHtml } from "@/api/endpoints/encuentros";
import { showToast } from "@/components/ui/Toast";

interface HtmlExportButtonProps {
  materiaId: string;
}

export function HtmlExportButton({ materiaId }: HtmlExportButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleExport = async () => {
    if (!materiaId) {
      showToast("Seleccioná una materia primero", "warning");
      return;
    }

    setIsLoading(true);
    try {
      const res = await generarHtml(materiaId);
      const html = typeof res.data === "string" ? res.data : String(res.data);

      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      showToast("HTML generado correctamente", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al generar HTML";
      showToast(msg, "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isLoading || !materiaId}
      className="px-4 py-2 text-sm rounded-md border border-border hover:bg-surface-variant disabled:opacity-50 transition-colors"
    >
      {isLoading ? "Generando..." : "Generar HTML"}
    </button>
  );
}
