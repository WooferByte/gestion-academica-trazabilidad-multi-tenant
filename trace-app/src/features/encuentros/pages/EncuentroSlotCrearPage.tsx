import { useNavigate, useSearchParams } from "react-router-dom";
import { useCrearSlot } from "@/features/encuentros/hooks/useEncuentrosSlots";
import { SlotForm } from "@/features/encuentros/components/SlotForm";
import { showToast } from "@/components/ui/Toast";
import type { SlotFormData } from "@/features/encuentros/types";
import type { SlotEncuentroCreate } from "@/api/types";

export default function EncuentroSlotCrearPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const crearMutation = useCrearSlot();

  const materiaId = searchParams.get("materia_id") || "";
  const asignacionId = searchParams.get("asignacion_id") || "";

  const handleSubmit = async (formData: SlotFormData) => {
    try {
      const asignacionIdValue = formData.asignacion_id || asignacionId || undefined;
      const payload = {
        ...formData,
        asignacion_id: asignacionIdValue,
        fecha_unica: formData.fecha_unica || null,
        meet_url: formData.meet_url || null,
      } as SlotEncuentroCreate;
      await crearMutation.mutateAsync(payload);
      showToast("Slot creado correctamente", "success");
      navigate("/encuentros");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
      const detail = axiosErr?.response?.data?.detail;
      let msg = "Error al crear el slot";
      if (typeof detail === "string") msg = detail;
      else if (Array.isArray(detail)) msg = detail.map((d: { msg?: string }) => d.msg).join("; ");
      else if (axiosErr?.message) msg = axiosErr.message;
      try { showToast(msg, "error"); } catch { /* fallback */ }
    }
  };

  return (
    <div className="space-y-lg p-lg max-w-2xl">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Nuevo Slot de Encuentro
      </h1>

      <div className="rounded-lg border border-border bg-surface p-6">
        <SlotForm
          initialData={materiaId ? { materia_id: materiaId, asignacion_id: asignacionId } : undefined}
          onSubmit={handleSubmit}
          isPending={crearMutation.isPending}
        />
      </div>
    </div>
  );
}
