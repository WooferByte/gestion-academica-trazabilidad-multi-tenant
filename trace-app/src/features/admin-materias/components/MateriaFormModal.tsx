import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog } from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useCrearMateria, useActualizarMateria, useMaterias } from "../hooks/useMaterias";
import type { Materia } from "../types/materia";

const materiaSchema = z.object({
  codigo: z.string().min(1, "El código es requerido"),
  nombre: z.string().min(1, "El nombre es requerido"),
});

type MateriaFormValues = z.infer<typeof materiaSchema>;

type MateriaFormModalProps = {
  open: boolean;
  onClose: () => void;
  materia?: Materia | null;
};

export function MateriaFormModal({ open, onClose, materia }: MateriaFormModalProps) {
  const isEdit = !!materia;
  const crearMutation = useCrearMateria();
  const actualizarMutation = useActualizarMateria();
  const { data: existingMaterias } = useMaterias();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    reset,
  } = useForm<MateriaFormValues>({
    resolver: zodResolver(materiaSchema),
    defaultValues: {
      codigo: "",
      nombre: "",
    },
  });

  useEffect(() => {
    if (open && materia) {
      reset({ codigo: materia.codigo, nombre: materia.nombre });
    }
    if (open && !materia) {
      reset({ codigo: "", nombre: "" });
    }
  }, [open, materia, reset]);

  const onSubmit = async (data: MateriaFormValues) => {
    const duplicate = existingMaterias?.find(
      (m) => m.codigo.toLowerCase() === data.codigo.toLowerCase() && m.id !== materia?.id,
    );
    if (duplicate) {
      setError("codigo", { message: "Ya existe una materia con este código" });
      return;
    }

    try {
      if (isEdit && materia) {
        await actualizarMutation.mutateAsync({ id: materia.id, data });
      } else {
        await crearMutation.mutateAsync(data);
      }
      reset();
      onClose();
    } catch {
      // error handled by query client
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={isEdit ? "Editar materia" : "Nueva materia"}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={isSubmitting}>
            {isSubmitting ? "Guardando..." : isEdit ? "Actualizar" : "Crear"}
          </Button>
        </>
      }
    >
      <form id="materia-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Código"
          placeholder="Ej: MAT-101"
          {...register("codigo")}
          error={errors.codigo?.message}
        />
        <Input
          label="Nombre"
          placeholder="Ej: Matemática I"
          {...register("nombre")}
          error={errors.nombre?.message}
        />
      </form>
    </Dialog>
  );
}
