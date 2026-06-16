import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useClonarEquipo } from "@/features/equipos/hooks/useClonarEquipo";
import { ClonarPreview } from "@/features/equipos/components/ClonarPreview";
import { showToast } from "@/components/ui/Toast";
import type { ClonarEquipoForm } from "@/features/equipos/types";

type Step = "origen" | "destino" | "preview";

export default function ClonarEquipoPage() {
  const [step, setStep] = useState<Step>("origen");
  const [form, setForm] = useState<ClonarEquipoForm>({
    origen: { materia_id: "", carrera_id: "", cohorte_id: "" },
    destino: { materia_id: "", carrera_id: "", cohorte_id: "", desde: "", hasta: "" },
  });

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

  const renderSelect = (field: "materia_id" | "carrera_id" | "cohorte_id", side: "origen" | "destino") => {
    const value = form[side][field];
    const setValue = (v: string) =>
      setForm((f) => ({ ...f, [side]: { ...f[side], [field]: v } }));
    const options = field === "materia_id" ? materias : field === "carrera_id" ? carreras : cohortes;
    const label = field.replace("_id", "").replace("_", " ");
    return (
      <div key={`${side}-${field}`}>
        <label className="block text-sm font-medium mb-1 capitalize">{label}</label>
        <select
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Seleccionar</option>
          {options.map((opt) => (
            <option key={opt.id} value={opt.id}>{opt.nombre}</option>
          ))}
        </select>
      </div>
    );
  };

  const mutation = useClonarEquipo();

  const handleNext = () => {
    if (step === "origen") setStep("destino");
    else if (step === "destino") setStep("preview");
  };

  const handleBack = () => {
    if (step === "destino") setStep("origen");
    else if (step === "preview") setStep("destino");
  };

  const handleConfirm = async () => {
    try {
      await mutation.mutateAsync(form);
      showToast("Equipo clonado exitosamente", "success");
      setForm({
        origen: { materia_id: "", carrera_id: "", cohorte_id: "" },
        destino: { materia_id: "", carrera_id: "", cohorte_id: "", desde: "", hasta: "" },
      });
      setStep("origen");
    } catch {
      showToast("Error al clonar el equipo", "error");
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Clonar Equipo Docente
      </h1>

      <div className="flex items-center gap-2 text-sm mb-4">
        {(["origen", "destino", "preview"] as Step[]).map((s, i) => (
          <span key={s} className="flex items-center gap-2">
            <span
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                step === s
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface-dimmed text-on-surface-variant"
              }`}
            >
              {i + 1}
            </span>
            <span className={step === s ? "text-on-surface font-medium" : "text-on-surface-variant"}>
              {s === "origen" ? "Origen" : s === "destino" ? "Destino" : "Previsualizar"}
            </span>
            {i < 2 && <span className="text-on-surface-variant mx-1">→</span>}
          </span>
        ))}
      </div>

      {step === "origen" && (
        <div className="max-w-lg space-y-4">
          <h2 className="text-lg font-medium">Seleccionar Equipo Origen</h2>
          {(["materia_id", "carrera_id", "cohorte_id"] as const).map((field) => renderSelect(field, "origen"))}
          <button
            onClick={handleNext}
            className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Siguiente
          </button>
        </div>
      )}

      {step === "destino" && (
        <div className="max-w-lg space-y-4">
          <h2 className="text-lg font-medium">Configurar Equipo Destino</h2>
          {(["materia_id", "carrera_id", "cohorte_id"] as const).map((field) => renderSelect(field, "destino"))}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Desde</label>
              <input
                type="date"
                value={form.destino.desde ?? ""}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    destino: { ...f.destino, desde: e.target.value },
                  }))
                }
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Hasta</label>
              <input
                type="date"
                value={form.destino.hasta ?? ""}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    destino: { ...f.destino, hasta: e.target.value },
                  }))
                }
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleBack}
              className="px-6 py-2 text-sm rounded-md border border-border hover:bg-surface-dimmed"
            >
              Volver
            </button>
            <button
              onClick={handleNext}
              className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Previsualizar
            </button>
          </div>
        </div>
      )}

      {step === "preview" && (
        <div className="max-w-lg space-y-4">
          <h2 className="text-lg font-medium">Confirmar Clonación</h2>
          <ClonarPreview
            origen={form.origen}
            destino={form.destino}
            isLoading={mutation.isPending}
          />
          <div className="flex gap-3">
            <button
              onClick={handleBack}
              className="px-6 py-2 text-sm rounded-md border border-border hover:bg-surface-dimmed"
            >
              Volver
            </button>
            <button
              onClick={handleConfirm}
              disabled={mutation.isPending}
              className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {mutation.isPending ? "Clonando..." : "Confirmar Clonación"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
