import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog } from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useCrearCarrera, useActualizarCarrera } from "../hooks/useCarreras";
import type { Carrera } from "../types/carrera";

const carreraSchema = z.object({
  codigo: z.string().min(1, "El código es requerido"),
  nombre: z.string().min(1, "El nombre es requerido"),
});

type CarreraFormValues = z.infer<typeof carreraSchema>;

type CarreraFormModalProps = {
  open: boolean;
  onClose: () => void;
  carrera?: Carrera | null;
};

export function CarreraFormModal({ open, onClose, carrera }: CarreraFormModalProps) {
  const isEdit = !!carrera;
  const crearMutation = useCrearCarrera();
  const actualizarMutation = useActualizarCarrera();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CarreraFormValues>({
    resolver: zodResolver(carreraSchema),
    defaultValues: {
      codigo: "",
      nombre: "",
    },
  });

  useEffect(() => {
    if (open && carrera) {
      reset({ codigo: carrera.codigo, nombre: carrera.nombre });
    }
    if (open && !carrera) {
      reset({ codigo: "", nombre: "" });
    }
  }, [open, carrera, reset]);

  const onSubmit = async (data: CarreraFormValues) => {
    try {
      if (isEdit && carrera) {
        await actualizarMutation.mutateAsync({ id: carrera.id, data });
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
      title={isEdit ? "Editar carrera" : "Nueva carrera"}
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
      <form id="carrera-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Código"
          placeholder="Ej: ING-2024"
          {...register("codigo")}
          error={errors.codigo?.message}
        />
        <Input
          label="Nombre"
          placeholder="Ej: Ingeniería en Sistemas"
          {...register("nombre")}
          error={errors.nombre?.message}
        />
      </form>
    </Dialog>
  );
}
