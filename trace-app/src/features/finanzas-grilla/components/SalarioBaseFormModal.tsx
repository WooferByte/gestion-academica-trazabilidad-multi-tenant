import { useState, useEffect } from "react";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import type { SalarioBaseCreateDTO } from "../types/grilla";

type SalarioBaseFormModalProps = {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: SalarioBaseCreateDTO) => void;
  isPending: boolean;
};

const ROLES = [
  { label: "Profesor", value: "PROFESOR" },
  { label: "Tutor", value: "TUTOR" },
  { label: "Nexo", value: "NEXO" },
  { label: "Coordinador", value: "COORDINADOR" },
];

const initialFormData: SalarioBaseCreateDTO = {
  rol: "",
  monto: 0,
  desde: "",
};

export function SalarioBaseFormModal({
  open,
  onClose,
  onSubmit,
  isPending,
}: SalarioBaseFormModalProps) {
  const [formData, setFormData] = useState<SalarioBaseCreateDTO>(initialFormData);

  useEffect(() => {
    if (open) {
      setFormData(initialFormData);
    }
  }, [open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="Nueva Base Salarial"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" form="salario-base-form" disabled={isPending}>
            {isPending ? "Creando..." : "Crear"}
          </Button>
        </>
      }
    >
      <form id="salario-base-form" onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="rol" className="text-sm font-medium text-gray-700">
            Rol
          </label>
          <select
            id="rol"
            value={formData.rol}
            onChange={(e) => setFormData((prev) => ({ ...prev, rol: e.target.value }))}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Seleccionar...</option>
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="monto" className="text-sm font-medium text-gray-700">
            Monto
          </label>
          <input
            id="monto"
            type="number"
            step="0.01"
            value={formData.monto || ""}
            onChange={(e) => setFormData((prev) => ({ ...prev, monto: parseFloat(e.target.value) || 0 }))}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="desde" className="text-sm font-medium text-gray-700">
            Vigencia desde
          </label>
          <input
            id="desde"
            type="date"
            value={formData.desde}
            onChange={(e) => setFormData((prev) => ({ ...prev, desde: e.target.value }))}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
      </form>
    </Dialog>
  );
}
