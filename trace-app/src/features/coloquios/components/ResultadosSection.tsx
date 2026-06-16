import { useState } from "react";
import { useResultadosList, useRegistrarResultado } from "@/features/coloquios/hooks/useColoquioResultados";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";

interface ResultadosSectionProps {
  evaluacionId: string;
}

export function ResultadosSection({ evaluacionId }: ResultadosSectionProps) {
  const { data, isLoading } = useResultadosList(evaluacionId);
  const registerMutation = useRegistrarResultado();
  const [notaInputs, setNotaInputs] = useState<Record<string, string>>({});

  const resultados = data?.items ?? [];

  const handleRegistrar = async (alumnoId: string) => {
    const nota = notaInputs[alumnoId];
    if (!nota?.trim()) {
      showToast("Ingresá una nota", "warning");
      return;
    }

    try {
      await registerMutation.mutateAsync({
        evaluacionId,
        alumnoId,
        data: { nota_final: nota },
      });
      showToast("Resultado registrado", "success");
      setNotaInputs((prev) => ({ ...prev, [alumnoId]: "" }));
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al registrar";
      showToast(msg, "error");
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="font-medium">Resultados</h3>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-variant/50">
                <th className="text-left px-4 py-3 font-medium">Alumno</th>
                <th className="text-left px-4 py-3 font-medium">Nota Final</th>
                <th className="text-left px-4 py-3 font-medium">Fecha</th>
                <th className="text-right px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {resultados.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center py-8 text-on-surface-variant">
                    No hay resultados registrados
                  </td>
                </tr>
              ) : (
                resultados.map((r) => (
                  <tr key={r.id}>
                    <td className="px-4 py-3">{r.alumno_id}</td>
                    <td className="px-4 py-3 font-medium">{r.nota_final}</td>
                    <td className="px-4 py-3 text-on-surface-variant">{r.created_at || "-"}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <input
                          type="text"
                          value={notaInputs[r.alumno_id] || ""}
                          onChange={(e) => setNotaInputs((prev) => ({ ...prev, [r.alumno_id]: e.target.value }))}
                          placeholder="Nota"
                          className="w-20 rounded border border-border bg-background px-2 py-1 text-sm"
                        />
                        <button
                          onClick={() => handleRegistrar(r.alumno_id)}
                          disabled={registerMutation.isPending}
                          className="text-xs px-2 py-1 rounded bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                        >
                          {registerMutation.isPending ? "..." : "Actualizar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
