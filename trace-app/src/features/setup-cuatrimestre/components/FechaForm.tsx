import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { showToast } from "@/components/ui/Toast";
import type { FechaAcademicaResponse } from "@/api/types";

interface FechaFormProps {
  onSave: (data: {
    materia_id: string;
    cohorte_id: string;
    tipo: string;
    numero: number;
    periodo: string;
    fecha: string;
    titulo: string;
  }) => Promise<void>;
  onCancel: () => void;
  editItem?: FechaAcademicaResponse;
  cohorteId?: string;
  isSubmitting?: boolean;
}

const tipos = ["parcial", "tp", "coloquio", "recuperatorio", "final"];

export function FechaForm({ onSave, onCancel, editItem, cohorteId, isSubmitting }: FechaFormProps) {
  const [materiaId, setMateriaId] = useState(editItem?.materia_id ?? "");
  const [cohorte, setCohorte] = useState(editItem?.cohorte_id ?? cohorteId ?? "");
  const [tipo, setTipo] = useState(editItem?.tipo ?? "parcial");
  const [numero, setNumero] = useState(editItem?.numero ?? 1);
  const [periodo, setPeriodo] = useState(editItem?.periodo ?? "");
  const [fecha, setFecha] = useState(editItem?.fecha ?? "");
  const [titulo, setTitulo] = useState(editItem?.titulo ?? "");

  const { data: materias } = useQuery({
    queryKey: ["fecha-materias"],
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

  const { data: cohortes } = useQuery({
    queryKey: ["fecha-cohortes"],
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
    if (!materiaId || !cohorte || !fecha || !titulo.trim()) {
      showToast("Completá todos los campos obligatorios", "error");
      return;
    }
    await onSave({
      materia_id: materiaId,
      cohorte_id: cohorte,
      tipo,
      numero,
      periodo: periodo || "2026",
      fecha,
      titulo: titulo.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
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
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Tipo</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            {tipos.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Nº Instancia</label>
          <input
            type="number"
            value={numero}
            onChange={(e) => setNumero(Number(e.target.value))}
            min={1}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Período</label>
          <input
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            placeholder="Ej: 2026"
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Fecha</label>
        <input
          type="date"
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          required
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Título</label>
        <input
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          required
          placeholder="Ej: 1er Parcial"
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
          {isSubmitting ? "Guardando..." : editItem ? "Actualizar" : "Crear Fecha"}
        </button>
      </div>
    </form>
  );
}
