import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useModificarVigencia } from "@/features/equipos/hooks/useModificarVigencia";
import { showToast } from "@/components/ui/Toast";

export default function VigenciaPage() {
  const [materiaId, setMateriaId] = useState("");
  const [carreraId, setCarreraId] = useState("");
  const [cohorteId, setCohorteId] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");

  const { data: materiasData } = useQuery({
    queryKey: ["materias", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/materias");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortesData } = useQuery({
    queryKey: ["cohortes", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/cohortes");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: carrerasData } = useQuery({
    queryKey: ["carreras", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/carreras");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const materias = useMemo(() => materiasData ?? [], [materiasData]);
  const cohortes = useMemo(() => cohortesData ?? [], [cohortesData]);
  const carreras = useMemo(() => carrerasData ?? [], [carrerasData]);

  const mutation = useModificarVigencia();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const result = await mutation.mutateAsync({
        materia_id: materiaId,
        carrera_id: carreraId || null,
        cohorte_id: cohorteId || null,
        desde: desde || null,
        hasta: hasta || null,
      });
      showToast(`Vigencia actualizada: ${result.filas_afectadas} filas afectadas`, "success");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const msg = axiosErr?.response?.data?.detail || "Error al actualizar la vigencia";
      showToast(msg, "error");
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Modificar Vigencia en Lote
      </h1>

      <form onSubmit={handleSubmit} className="max-w-lg space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Materia *</label>
          <select
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            required
          >
            <option value="">Seleccionar</option>
            {materias.map((m) => (
              <option key={m.id} value={m.id}>{m.nombre}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Carrera</label>
          <select
            value={carreraId}
            onChange={(e) => setCarreraId(e.target.value)}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccionar</option>
            {carreras.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
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
            <option value="">Seleccionar</option>
            {cohortes.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Desde</label>
            <input
              type="date"
              value={desde}
              onChange={(e) => setDesde(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Hasta</label>
            <input
              type="date"
              value={hasta}
              onChange={(e) => setHasta(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {mutation.isPending ? "Actualizando..." : "Actualizar Vigencia"}
        </button>
      </form>
    </div>
  );
}
