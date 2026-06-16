import { useParams, useNavigate } from "react-router-dom";
import { useCrearAviso } from "@/features/avisos/hooks/useCrearAviso";
import { useActualizarAviso } from "@/features/avisos/hooks/useActualizarAviso";
import { useQuery } from "@tanstack/react-query";
import { obtenerAviso } from "@/api/endpoints/avisos";
import { AvisoForm } from "@/features/avisos/components/AvisoForm";
import { showToast } from "@/components/ui/Toast";
import type { AvisoFormData } from "@/features/avisos/types";

export default function AvisoFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = !!id;

  const crearMutation = useCrearAviso();
  const actualizarMutation = useActualizarAviso();

  const { data: existingAviso, isLoading: isLoadingExisting } = useQuery({
    queryKey: ["aviso", id],
    queryFn: async () => {
      if (!id) return null;
      const res = await obtenerAviso(id);
      return res.data;
    },
    enabled: isEditing,
  });

  const handleSubmit = async (formData: AvisoFormData) => {
    try {
      if (isEditing && id) {
        await actualizarMutation.mutateAsync({
          id,
          data: {
            alcance: formData.alcance,
            materia_id: formData.materia_id || null,
            cohorte_id: formData.cohorte_id || null,
            rol_destino: formData.rol_destino || null,
            severidad: formData.severidad,
            titulo: formData.titulo,
            cuerpo: formData.cuerpo,
            inicio_vigencia: formData.inicio_vigencia,
            fin_vigencia: formData.fin_vigencia,
            orden: formData.orden,
            requiere_ack: formData.requiere_ack,
          },
        });
        showToast("Aviso actualizado", "success");
      } else {
        await crearMutation.mutateAsync({
          alcance: formData.alcance,
          materia_id: formData.materia_id || null,
          cohorte_id: formData.cohorte_id || null,
          rol_destino: formData.rol_destino || null,
          severidad: formData.severidad,
          titulo: formData.titulo,
          cuerpo: formData.cuerpo,
          inicio_vigencia: formData.inicio_vigencia,
          fin_vigencia: formData.fin_vigencia,
          orden: formData.orden,
          requiere_ack: formData.requiere_ack,
        });
        showToast("Aviso creado", "success");
      }
      navigate("/avisos");
    } catch (err: unknown) {
      console.error("Error guardando aviso:", err);
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al guardar el aviso";
      showToast(msg, "error");
    }
  };

  const initialData: Partial<AvisoFormData> | undefined = existingAviso
    ? {
        alcance: existingAviso.alcance,
        materia_id: existingAviso.materia_id ?? undefined,
        cohorte_id: existingAviso.cohorte_id ?? undefined,
        rol_destino: existingAviso.rol_destino ?? undefined,
        severidad: existingAviso.severidad,
        titulo: existingAviso.titulo,
        cuerpo: existingAviso.cuerpo,
        inicio_vigencia: existingAviso.inicio_vigencia,
        fin_vigencia: existingAviso.fin_vigencia,
        orden: existingAviso.orden,
        requiere_ack: existingAviso.requiere_ack,
      }
    : undefined;

  if (isEditing && isLoadingExisting) {
    return (
      <div className="space-y-lg p-lg">
        <p className="text-on-surface-variant">Cargando aviso...</p>
      </div>
    );
  }

  return (
    <div className="space-y-lg p-lg max-w-2xl">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        {isEditing ? "Editar Aviso" : "Nuevo Aviso"}
      </h1>

      <AvisoForm
        initialData={initialData}
        onSubmit={handleSubmit}
        isPending={crearMutation.isPending || actualizarMutation.isPending}
      />
    </div>
  );
}
