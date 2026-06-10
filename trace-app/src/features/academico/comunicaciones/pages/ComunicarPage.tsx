import { useState, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { useComunicacionPreview } from "@/features/academico/comunicaciones/hooks/useComunicacionPreview";
import { useEnviarComunicacion } from "@/features/academico/comunicaciones/hooks/useEnviarComunicacion";
import { useEnviarLote } from "@/features/academico/comunicaciones/hooks/useEnviarLote";
import { useCancelarComunicacion } from "@/features/academico/comunicaciones/hooks/useCancelarComunicacion";
import { MessageComposer } from "@/features/academico/comunicaciones/components/MessageComposer";
import { PreviewPanel } from "@/features/academico/comunicaciones/components/PreviewPanel";
import { TrackingTable } from "@/features/academico/comunicaciones/components/TrackingTable";
import { LoteApprovalPanel } from "@/features/academico/comunicaciones/components/LoteApprovalPanel";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useComunicacionesTracking } from "@/features/academico/comunicaciones/hooks/useComunicacionesTracking";
import { Button } from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import type { ComunicacionPreviewResponse } from "@/api/types";

type CommStep = "compose" | "tracking" | "approval";

export default function ComunicarPage() {
  const location = useLocation();
  const { permissions } = useAuth();

  const selectedAlumnos = (location.state as { selectedAlumnos?: string[] })?.selectedAlumnos ?? [];
  const [asunto, setAsunto] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [previewData, setPreviewData] = useState<ComunicacionPreviewResponse | null>(null);
  const [messageChanged, setMessageChanged] = useState(false);
  const [loteId, setLoteId] = useState<string | null>(null);
  const [step, setStep] = useState<CommStep>("compose");

  const previewMutation = useComunicacionPreview();
  const enviarMutation = useEnviarComunicacion();
  const enviarLoteMutation = useEnviarLote();
  const cancelarMutation = useCancelarComunicacion();

  const tracking = useComunicacionesTracking(loteId ?? "");

  const canApprove = permissions.includes("comunicacion:aprobar");
  const primerDestinatario = selectedAlumnos[0] ?? "";

  const handlePreview = useCallback(async () => {
    if (!asunto.trim() || !mensaje.trim()) return;
    try {
      const result = await previewMutation.mutateAsync({
        destinatario: primerDestinatario,
        asunto,
        cuerpo: mensaje,
      });
      setPreviewData(result);
      setMessageChanged(false);
    } catch {
      showToast("Error al generar vista previa", "error");
    }
  }, [asunto, mensaje, primerDestinatario, previewMutation]);

  const handleSend = useCallback(async () => {
    if (!primerDestinatario) return;
    try {
      const result = await enviarMutation.mutateAsync({
        destinatario: primerDestinatario,
        asunto,
        cuerpo: mensaje,
      });
      showToast("Comunicación enviada", "success");
      setLoteId(result.lote_id);
      setStep("tracking");
    } catch {
      showToast("Error al enviar", "error");
    }
  }, [primerDestinatario, asunto, mensaje, enviarMutation]);

  const handleSendLote = useCallback(async () => {
    if (!selectedAlumnos.length) return;
    try {
      const results = await enviarLoteMutation.mutateAsync({
        destinatarios: selectedAlumnos,
        asunto,
        cuerpo: mensaje,
      });
      showToast("Lote enviado para aprobación", "success");
      setLoteId(results[0]?.lote_id ?? null);
      setStep("tracking");
    } catch {
      showToast("Error al enviar lote", "error");
    }
  }, [selectedAlumnos, asunto, mensaje, enviarLoteMutation]);

  const handleCancel = useCallback(async (id: string) => {
    try {
      await cancelarMutation.mutateAsync(id);
      showToast("Comunicación cancelada", "success");
    } catch {
      showToast("Error al cancelar", "error");
    }
  }, [cancelarMutation]);

  return (
    <div className="space-y-lg p-lg">
      <nav className="flex items-center gap-xs font-body-sm text-body-sm text-on-surface-variant">
        <span><a href="/academico" className="hover:text-primary transition-colors">Académico</a></span>
        <span className="material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface">Comunicar</span>
      </nav>

      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">Comunicar</h1>
        {canApprove && (
          <div className="flex gap-sm">
            <Button
              variant={step === "compose" ? "primary" : "secondary"}
              onClick={() => setStep("compose")}
            >
              Redactar
            </Button>
            <Button
              variant={step === "approval" ? "primary" : "secondary"}
              onClick={() => setStep("approval")}
            >
              Aprobaciones
            </Button>
            <Button
              variant={step === "tracking" ? "primary" : "secondary"}
              onClick={() => setStep("tracking")}
            >
              Seguimiento
            </Button>
          </div>
        )}
      </div>

      {step === "compose" && (
        <div className="grid gap-lg lg:grid-cols-2">
          <div className="space-y-md">
            <MessageComposer
              destinatariosCount={selectedAlumnos.length}
              asunto={asunto}
              onAsuntoChange={(val) => {
                setAsunto(val);
                if (previewData) setMessageChanged(true);
              }}
              mensaje={mensaje}
              onMensajeChange={(msg) => {
                setMensaje(msg);
                if (previewData) setMessageChanged(true);
              }}
            />
            <Button
              onClick={handlePreview}
              disabled={!asunto.trim() || !mensaje.trim() || previewMutation.isPending}
            >
              {previewMutation.isPending ? "Generando..." : "Vista previa"}
            </Button>
            {messageChanged && (
              <p className="font-body-sm text-body-sm text-warning">
                Debe generar una nueva vista previa
              </p>
            )}
          </div>

          <PreviewPanel
            preview={previewData}
            isPreviewLoading={previewMutation.isPending}
            onSend={handleSend}
            onSendLote={handleSendLote}
            canApprove={canApprove}
          />
        </div>
      )}

      {step === "tracking" && loteId && (
        <div className="space-y-md">
          <h2 className="font-label-lg text-label-lg text-on-surface">Seguimiento</h2>
          {tracking.data?.lote_estado === "pendiente" && canApprove && (
            <div className="rounded-lg bg-yellow-50 p-md font-body-sm text-body-sm text-yellow-800">
              Este envío requiere aprobación de un coordinador
            </div>
          )}
          <TrackingTable
            items={tracking.data?.items ?? []}
            onCancel={handleCancel}
          />
        </div>
      )}

      {step === "approval" && canApprove && (
        <div className="space-y-md">
          <h2 className="font-label-lg text-label-lg text-on-surface">Aprobaciones pendientes</h2>
          <LoteApprovalPanel />
        </div>
      )}
    </div>
  );
}
