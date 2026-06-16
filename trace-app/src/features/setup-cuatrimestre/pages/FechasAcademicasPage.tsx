import { useState, useMemo, useCallback } from "react";
import {
  useFechasList,
  useCrearFecha,
  useActualizarFecha,
  useEliminarFecha,
} from "@/features/setup-cuatrimestre/hooks/useFechasAcademicas";
import { SelectorCarreraCohorte } from "@/features/setup-cuatrimestre/components/SelectorCarreraCohorte";
import { FechaForm } from "@/features/setup-cuatrimestre/components/FechaForm";
import { FechasTable } from "@/features/setup-cuatrimestre/components/FechasTable";
import { FechasCalendar } from "@/features/setup-cuatrimestre/components/FechasCalendar";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { FechaAcademicaResponse } from "@/api/types";

const tipoFiltros = ["", "parcial", "tp", "coloquio", "recuperatorio", "final"];

export default function FechasAcademicasPage() {
  const [carreraId, setCarreraId] = useState("");
  const [cohorteId, setCohorteId] = useState("");
  const [tipoFiltro, setTipoFiltro] = useState("");
  const [view, setView] = useState<"table" | "calendar">("table");
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<FechaAcademicaResponse | null>(null);

  const { data, isLoading } = useFechasList(
    carreraId || cohorteId || tipoFiltro
      ? {
          materia_id: carreraId || undefined,
          cohorte_id: cohorteId || undefined,
          tipo: tipoFiltro || undefined,
        }
      : undefined,
  );

  const createMutation = useCrearFecha();
  const updateMutation = useActualizarFecha();
  const deleteMutation = useEliminarFecha();

  const items = useMemo(() => {
    if (!data?.items) return [];
    return data.items;
  }, [data]);

  const handleSave = async (formData: {
    materia_id: string;
    cohorte_id: string;
    tipo: string;
    numero: number;
    periodo: string;
    fecha: string;
    titulo: string;
  }) => {
    try {
      if (editItem) {
        await updateMutation.mutateAsync({
          id: editItem.id,
          data: {
            tipo: formData.tipo,
            numero: formData.numero,
            periodo: formData.periodo,
            fecha: formData.fecha,
            titulo: formData.titulo,
          },
        });
        showToast("Fecha actualizada", "success");
      } else {
        await createMutation.mutateAsync(formData);
        showToast("Fecha creada", "success");
      }
      setShowForm(false);
      setEditItem(null);
    } catch {
      showToast("Error al guardar la fecha", "error");
    }
  };

  const handleEdit = useCallback((item: FechaAcademicaResponse) => {
    setEditItem(item);
    setShowForm(true);
  }, []);

  const handleDelete = (item: FechaAcademicaResponse) => {
    if (window.confirm(`¿Estás seguro de eliminar "${item.titulo}"?`)) {
      deleteMutation.mutate(item.id, {
        onSuccess: () => showToast("Fecha eliminada", "success"),
        onError: () => showToast("Error al eliminar", "error"),
      });
    }
  };

  return (
    <div className="space-y-lg">
      <div className="flex items-center justify-between">
        <h2 className="font-headline-sm text-headline-sm text-on-surface">
          Fechas Académicas
        </h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setView("table")}
            className={`px-4 py-2 text-sm rounded-md ${
              view === "table"
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "border border-border hover:bg-accent"
            }`}
          >
            Tabla
          </button>
          <button
            type="button"
            onClick={() => setView("calendar")}
            className={`px-4 py-2 text-sm rounded-md ${
              view === "calendar"
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "border border-border hover:bg-accent"
            }`}
          >
            Calendario
          </button>
          {!showForm && (
            <button
              type="button"
              onClick={() => {
                setEditItem(null);
                setShowForm(true);
              }}
              className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Nueva Fecha
            </button>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-4 space-y-4">
        <SelectorCarreraCohorte
          carreraId={carreraId}
          cohorteId={cohorteId}
          onCarreraChange={setCarreraId}
          onCohorteChange={setCohorteId}
        />
        <div>
          <label className="block text-sm font-medium mb-1">Tipo</label>
          <select
            value={tipoFiltro}
            onChange={(e) => setTipoFiltro(e.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Todos</option>
            {tipoFiltros.filter(Boolean).map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {showForm && (
        <div className="rounded-lg border border-border bg-surface p-6">
          <FechaForm
            onSave={handleSave}
            onCancel={() => { setShowForm(false); setEditItem(null); }}
            editItem={editItem ?? undefined}
            cohorteId={cohorteId || undefined}
            isSubmitting={createMutation.isPending || updateMutation.isPending}
          />
        </div>
      )}

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : view === "calendar" ? (
        <FechasCalendar items={items} onEdit={handleEdit} />
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <FechasTable
            items={items}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      )}
    </div>
  );
}
