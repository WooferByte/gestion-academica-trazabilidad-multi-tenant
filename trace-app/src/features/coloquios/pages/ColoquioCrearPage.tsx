import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useCrearConvocatoria } from "@/features/coloquios/hooks/useColoquios";
import { TurnoForm } from "@/features/coloquios/components/TurnoForm";
import { TurnoList } from "@/features/coloquios/components/TurnoList";
import { showToast } from "@/components/ui/Toast";
import type { TurnoFormData } from "@/features/coloquios/types";

interface SelectOption {
  id: string;
  nombre: string;
}

export default function ColoquioCrearPage() {
  const navigate = useNavigate();
  const crearMutation = useCrearConvocatoria();

  const { data: materiasData } = useQuery({
    queryKey: ["materias", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/materias");
        return (res.data?.items ?? []) as SelectOption[];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortesData } = useQuery({
    queryKey: ["cohortes", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/cohortes");
        return (res.data?.items ?? []) as SelectOption[];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const materias = useMemo(() => materiasData ?? [], [materiasData]);
  const cohortes = useMemo(() => cohortesData ?? [], [cohortesData]);

  const [materiaId, setMateriaId] = useState("");
  const [cohorteId, setCohorteId] = useState("");
  const [instancia, setInstancia] = useState("");
  const [tipo, setTipo] = useState("Parcial");
  const [turnos, setTurnos] = useState<TurnoFormData[]>([]);

  const handleAddTurno = (turno: TurnoFormData) => {
    setTurnos((prev) => [...prev, turno]);
  };

  const handleRemoveTurno = (index: number) => {
    setTurnos((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!materiaId || !cohorteId || !instancia) {
      showToast("Completá todos los campos obligatorios", "warning");
      return;
    }

    if (turnos.length === 0) {
      showToast("Debe agregar al menos un turno", "warning");
      return;
    }

    try {
      const result = await crearMutation.mutateAsync({
        materia_id: materiaId,
        cohorte_id: cohorteId,
        instancia,
        tipo,
        turnos,
      });
      showToast("Convocatoria creada", "success");
      navigate(`/coloquios/${result.id}`);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al crear";
      showToast(msg, "error");
    }
  };

  return (
    <div className="space-y-lg p-lg max-w-2xl">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Nueva Convocatoria
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="rounded-lg border border-border bg-surface p-6 space-y-4">
          <h2 className="font-title-md text-title-md">Datos Generales</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Materia *</label>
              <select
                value={materiaId}
                onChange={(e) => setMateriaId(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Seleccionar materia</option>
                {materias.map((m) => (
                  <option key={m.id} value={m.id}>{m.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Cohorte *</label>
              <select
                value={cohorteId}
                onChange={(e) => setCohorteId(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Seleccionar cohorte</option>
                {cohortes.map((c) => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Instancia *</label>
            <input
              type="text"
              value={instancia}
              onChange={(e) => setInstancia(e.target.value)}
              placeholder="Ej: 1er Parcial, Final, Recuperatorio"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Tipo</label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="final">Final</option>
              <option value="Parcial">Parcial</option>
              <option value="Coloquio">Coloquio</option>
              <option value="recuperatorio">Recuperatorio</option>
              <option value="integrador">Integrador</option>
            </select>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-6 space-y-4">
          <h2 className="font-title-md text-title-md">Turnos</h2>
          <TurnoForm onAdd={handleAddTurno} />
          <TurnoList turnos={turnos} onRemove={handleRemoveTurno} isEditable />
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => navigate("/coloquios")}
            className="px-6 py-2 text-sm rounded-md border border-border hover:bg-surface-variant"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={crearMutation.isPending}
            className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {crearMutation.isPending ? "Creando..." : "Crear Convocatoria"}
          </button>
        </div>
      </form>
    </div>
  );
}
