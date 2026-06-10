import { Button } from "@/components/ui/Button";
import type { ComunicacionPreviewResponse } from "@/api/types";

type PreviewPanelProps = {
  preview: ComunicacionPreviewResponse | null;
  isPreviewLoading: boolean;
  onSend: () => void;
  onSendLote: () => void;
  canApprove: boolean;
};

export function PreviewPanel({
  preview,
  isPreviewLoading,
  onSend,
  onSendLote,
  canApprove,
}: PreviewPanelProps) {
  if (isPreviewLoading) {
    return (
      <div className="flex items-center justify-center rounded-xl border border-outline-variant p-xl">
        <span className="material-symbols-outlined animate-spin text-secondary">
          progress_activity
        </span>
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="flex flex-col items-center gap-md rounded-xl border border-outline-variant p-xl text-center">
        <span className="material-symbols-outlined text-3xl text-secondary">visibility</span>
        <p className="font-body-md text-body-md text-on-surface-variant">
          Generá una vista previa antes de enviar
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-md rounded-xl border border-outline-variant bg-white p-lg">
      <h3 className="font-label-lg text-label-lg text-on-surface">Vista previa</h3>

      <div className="rounded-lg border border-outline-variant bg-surface-container p-md">
        <p className="font-label-md text-label-md text-on-surface mb-xs">{preview.asunto_renderizado}</p>
        <div
          className="font-body-md text-body-md"
          dangerouslySetInnerHTML={{ __html: preview.cuerpo_renderizado }}
        />
      </div>

      {preview.variables_no_encontradas.length > 0 && (
        <div className="font-body-sm text-body-sm text-warning">
          <p>Variables no encontradas: {preview.variables_no_encontradas.join(", ")}</p>
        </div>
      )}

      <div className="flex gap-md">
        <Button onClick={onSend}>Enviar</Button>
        {canApprove && (
          <Button variant="secondary" onClick={onSendLote}>
            Enviar lote
          </Button>
        )}
      </div>
    </div>
  );
}
