import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog } from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import { useCrearCohorte, useActualizarCohorte } from "../hooks/useCohortes";
import { useCarreras } from "@/features/admin-carreras/hooks/useCarreras";
import type { Cohorte } from "../types/cohorte";

const cohorteSchema = z.object({
  nombre: z.string().min(1, "El nombre es requerido"),
  carrera_id: z.string().min(1, "Seleccioná una carrera"),
  anio: z.coerce.number().int().min(2000, "Año inválido").max(2100, "Año inválido"),
  vig_desde: z.string().min(1, "La fecha de inicio es requerida"),
  vig_hasta: z.string().min(1, "La fecha de fin es requerida"),
});

type CohorteFormValues = z.infer<typeof cohorteSchema>;

type CohorteFormModalProps = {
  open: boolean;
  onClose: () => void;
  cohorte?: Cohorte | null;
};

export function CohorteFormModal({ open, onClose, cohorte }: CohorteFormModalProps) {
  const isEdit = !!cohorte;
  const crearMutation = useCrearCohorte();
  const actualizarMutation = useActualizarCohorte();
  const { data: carreras } = useCarreras({ activo: true });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CohorteFormValues>({
    resolver: zodResolver(cohorteSchema),
    defaultValues: {
      nombre: "",
      carrera_id: "",
      anio: new Date().getFullYear(),
      vig_desde: "",
      vig_hasta: "",
    },
  });

  useEffect(() => {
    if (open && cohorte) {
      reset({
        nombre: cohorte.nombre,
        carrera_id: cohorte.carrera_id,
        anio: cohorte.anio,
        vig_desde: cohorte.vig_desde,
        vig_hasta: cohorte.vig_hasta,
      });
    }
    if (open && !cohorte) {
      reset({
        nombre: "",
        carrera_id: "",
        anio: new Date().getFullYear(),
        vig_desde: "",
        vig_hasta: "",
      });
    }
  }, [open, cohorte, reset]);

  const onSubmit = async (data: CohorteFormValues) => {
    try {
      if (isEdit && cohorte) {
        const { carrera_id, ...editData } = data;
        await actualizarMutation.mutateAsync({ id: cohorte.id, data: editData });
      } else {
        await crearMutation.mutateAsync(data);
      }
      reset();
      onClose();
      showToast(isEdit ? "Cohorte actualizada" : "Cohorte creada", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al guardar la cohorte";
      showToast(msg, "error");
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={isEdit ? "Editar cohorte" : "Nuevo cohorte"}
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
      <form id="cohorte-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Nombre"
          placeholder="Ej: Cohorte 2024"
          {...register("nombre")}
          error={errors.nombre?.message}
        />
        <div className="flex flex-col gap-xs">
          <label htmlFor="carrera_id" className="font-label-md text-label-md text-on-surface">
            Carrera
          </label>
          <select
            id="carrera_id"
            className="h-10 w-full rounded border bg-white px-md py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
            {...register("carrera_id")}
          >
            <option value="">Seleccioná una carrera</option>
            {carreras?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          {errors.carrera_id?.message && (
            <p className="font-label-sm text-label-sm text-error">{errors.carrera_id.message}</p>
          )}
        </div>
        <Input
          label="Año"
          type="number"
          placeholder="Ej: 2024"
          {...register("anio")}
          error={errors.anio?.message}
        />
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Vigencia desde"
            type="date"
            {...register("vig_desde")}
            error={errors.vig_desde?.message}
          />
          <Input
            label="Vigencia hasta"
            type="date"
            {...register("vig_hasta")}
            error={errors.vig_hasta?.message}
          />
        </div>
      </form>
    </Dialog>
  );
}
