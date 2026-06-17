import { useState, useEffect } from "react";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import type { CategoriaPlus, CategoriaPlusCreateDTO } from "../types/grilla";

type FormData = CategoriaPlusCreateDTO;

type CategoriaPlusFormModalProps = {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: FormData) => void;
  isPending: boolean;
  categoria?: CategoriaPlus | null;
};

const initialFormData: FormData = {
  codigo: "",
  nombre: "",
  activo: true,
};

export function CategoriaPlusFormModal({
  open,
  onClose,
  onSubmit,
  isPending,
  categoria,
}: CategoriaPlusFormModalProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData);

  useEffect(() => {
    if (open) {
      setFormData(
        categoria
          ? { codigo: categoria.codigo, nombre: categoria.nombre, activo: categoria.activo }
          : initialFormData,
      );
    }
  }, [open, categoria]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={categoria ? "Editar Categoría Plus" : "Nueva Categoría Plus"}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" form="categoria-plus-form" disabled={isPending}>
            {isPending ? "Guardando..." : categoria ? "Guardar" : "Crear"}
          </Button>
        </>
      }
    >
      <form id="categoria-plus-form" onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="codigo" className="text-sm font-medium text-gray-700">
            Código
          </label>
          <input
            id="codigo"
            type="text"
            value={formData.codigo}
            onChange={(e) => setFormData((prev) => ({ ...prev, codigo: e.target.value }))}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="nombre" className="text-sm font-medium text-gray-700">
            Nombre
          </label>
          <input
            id="nombre"
            type="text"
            value={formData.nombre}
            onChange={(e) => setFormData((prev) => ({ ...prev, nombre: e.target.value }))}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
      </form>
    </Dialog>
  );
}
