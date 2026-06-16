import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAvisos } from "@/features/avisos/hooks/useAvisos";
import { useEliminarAviso } from "@/features/avisos/hooks/useEliminarAviso";
import { AvisoTable } from "@/features/avisos/components/AvisoTable";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { AvisoResponse } from "@/api/types";

export default function AvisosListPage() {
  const navigate = useNavigate();
  const [filterActivo, setFilterActivo] = useState<string>("todos");
  const [filterAlcance, setFilterAlcance] = useState<string>("");

  const { data, isLoading } = useAvisos();
  const deleteMutation = useEliminarAviso();

  const items = (data?.items ?? []).filter((a) => {
    if (filterActivo === "activos" && !a.activo) return false;
    if (filterActivo === "inactivos" && a.activo) return false;
    if (filterAlcance && a.alcance !== filterAlcance) return false;
    return true;
  });

  const handleEdit = (item: AvisoResponse) => {
    navigate(`/avisos/editar/${item.id}`);
  };

  const handleDelete = (item: AvisoResponse) => {
    if (window.confirm("¿Estás seguro de desactivar este aviso?")) {
      deleteMutation.mutate(item.id, {
        onSuccess: () => showToast("Aviso desactivado", "success"),
        onError: () => showToast("Error al desactivar el aviso", "error"),
      });
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Avisos
        </h1>
        <button
          onClick={() => navigate("/avisos/crear")}
          className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Nuevo Aviso
        </button>
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Estado</label>
          <select
            value={filterActivo}
            onChange={(e) => setFilterActivo(e.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="todos">Todos</option>
            <option value="activos">Activos</option>
            <option value="inactivos">Inactivos</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Alcance</label>
          <select
            value={filterAlcance}
            onChange={(e) => setFilterAlcance(e.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Todos</option>
            <option value="Global">Global</option>
            <option value="PorMateria">Por Materia</option>
            <option value="PorCohorte">Por Cohorte</option>
            <option value="PorRol">Por Rol</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <AvisoTable
            items={items}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      )}
    </div>
  );
}
