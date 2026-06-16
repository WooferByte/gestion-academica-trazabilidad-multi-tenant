import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { showToast } from "@/components/ui/Toast";
import type { ProgramaMateriaResponse } from "@/api/types";

interface ProgramaFormProps {
  onSave: (data: {
    materia_id: string;
    carrera_id: string;
    cohorte_id: string;
    titulo: string;
  }) => Promise<void>;
  onCancel: () => void;
  editItem?: ProgramaMateriaResponse;
  carreraId?: string;
  cohorteId?: string;
  isSubmitting?: boolean;
}

export function ProgramaForm({ onSave, onCancel, editItem, carreraId, cohorteId, isSubmitting }: ProgramaFormProps) {
  const [materiaId, setMateriaId] = useState(editItem?.materia_id ?? "");
  const [carrera, setCarrera] = useState(editItem?.carrera_id ?? carreraId ?? "");
  const [cohorte, setCohorte] = useState(editItem?.cohorte_id ?? cohorteId ?? "");
  const [titulo, setTitulo] = useState(editItem?.titulo ?? "");

  const { data: materias } = useQuery({
    queryKey: ["prog-materias"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string }[] }>("/admin/materias");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: carreras } = useQuery({
    queryKey: ["prog-carreras"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string }[] }>("/admin/carreras");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortes } = useQuery({
    queryKey: ["prog-cohortes"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string; anio: number }[] }>("/admin/cohortes");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titulo.trim()) {
      showToast("El título es obligatorio", "error");
      return;
    }
    await onSave({
      materia_id: materiaId,
      carrera_id: carrera,
      cohorte_id: cohorte,
      titulo: titulo.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Materia</label>
        <select
          value={materiaId}
          onChange={(e) => setMateriaId(e.target.value)}
          required
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Seleccioná una materia</option>
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Carrera</label>
          <select
            value={carrera}
            onChange={(e) => setCarrera(e.target.value)}
            required
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccioná una carrera</option>
            {carreras?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Cohorte</label>
          <select
            value={cohorte}
            onChange={(e) => setCohorte(e.target.value)}
            required
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccioná una cohorte</option>
            {cohortes?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Título del Programa</label>
        <input
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          required
          placeholder="Ej: Programa de Álgebra 2026"
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
      </div>
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm rounded-md border border-border hover:bg-accent"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isSubmitting ? "Guardando..." : editItem ? "Actualizar" : "Crear Programa"}
        </button>
      </div>
    </form>
  );
}
