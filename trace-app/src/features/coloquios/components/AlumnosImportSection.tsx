import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useImportarAlumnos } from "@/features/coloquios/hooks/useColoquioAlumnos";
import { showToast } from "@/components/ui/Toast";

interface AlumnosImportSectionProps {
  evaluacionId: string;
}

export function AlumnosImportSection({ evaluacionId }: AlumnosImportSectionProps) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const importMutation = useImportarAlumnos();

  const { data: usuariosData } = useQuery({
    queryKey: ["usuarios", "alumnos"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/usuarios");
        const items = (res.data?.items ?? []) as { id: string; nombre: string; apellido: string; email: string; roles: string[] }[];
        return items.filter((u) => u.roles?.includes("alumno") || u.roles?.includes("ALUMNO"));
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const alumnos = useMemo(() => usuariosData ?? [], [usuariosData]);

  const toggleAlumno = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const handleImport = async () => {
    if (selectedIds.length === 0) {
      showToast("Seleccioná al menos un alumno", "warning");
      return;
    }

    try {
      await importMutation.mutateAsync({ evaluacionId, alumnoIds: selectedIds });
      showToast(`${selectedIds.length} alumno(s) importado(s)`, "success");
      setSelectedIds([]);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al importar";
      showToast(msg, "error");
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="font-medium">Importar Alumnos</h3>
      <p className="text-sm text-on-surface-variant">
        Seleccioná los alumnos a importar:
      </p>
      {alumnos.length === 0 ? (
        <p className="text-sm text-on-surface-variant">Cargando alumnos...</p>
      ) : (
        <div className="max-h-48 overflow-y-auto border border-border rounded-md divide-y divide-border">
          {alumnos.map((a) => (
            <label
              key={a.id}
              className="flex items-center gap-2 px-3 py-2 hover:bg-surface-dimmed cursor-pointer text-sm"
            >
              <input
                type="checkbox"
                checked={selectedIds.includes(a.id)}
                onChange={() => toggleAlumno(a.id)}
                className="rounded"
              />
              <span>{a.nombre} {a.apellido} ({a.email})</span>
            </label>
          ))}
        </div>
      )}
      <div className="flex items-center gap-3">
        <button
          onClick={handleImport}
          disabled={importMutation.isPending || selectedIds.length === 0}
          className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {importMutation.isPending ? "Importando..." : `Importar (${selectedIds.length})`}
        </button>
        {selectedIds.length > 0 && (
          <span className="text-sm text-on-surface-variant">
            {selectedIds.length} seleccionado(s)
          </span>
        )}
      </div>
    </div>
  );
}
