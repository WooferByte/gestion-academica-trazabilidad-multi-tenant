import { useQuery } from "@tanstack/react-query";
import { useAprobarLote } from "@/features/academico/comunicaciones/hooks/useAprobarLote";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { showToast } from "@/components/ui/Toast";
import api from "@/api/client";

interface LotePendiente {
  id: string;
  mensaje_preview: string;
  total_destinatarios: number;
  estado: string;
  creado: string;
}

export function LoteApprovalPanel() {
  const { data, isLoading, refetch } = useQuery<LotePendiente[]>({
    queryKey: ["comunicaciones-pendientes"],
    queryFn: async () => {
      const res = await api.get<LotePendiente[]>("/comunicaciones/lotes/pendientes");
      return res.data;
    },
  });

  const aprobarMutation = useAprobarLote();

  function handleApprove(loteId: string) {
    aprobarMutation.mutate(loteId, {
      onSuccess: () => {
        showToast("Lote aprobado", "success");
        refetch();
      },
      onError: (err: Error) => showToast(err.message, "error"),
    });
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-xl">
        <span className="material-symbols-outlined animate-spin text-secondary">
          progress_activity
        </span>
      </div>
    );
  }

  const lotes = data ?? [];

  if (lotes.length === 0) {
    return (
      <div className="flex flex-col items-center gap-md rounded-xl border border-outline-variant p-xl text-center">
        <span className="material-symbols-outlined text-3xl text-green-600">fact_check</span>
        <p className="font-body-lg text-body-lg text-on-surface">No hay lotes pendientes de aprobación</p>
      </div>
    );
  }

  return (
    <div className="space-y-md">
      {lotes.map((lote) => (
        <div
          key={lote.id}
          className="flex items-start justify-between rounded-xl border border-outline-variant bg-white p-lg"
        >
          <div className="space-y-sm flex-1">
            <div className="flex items-center gap-sm">
              <span className="font-label-md text-label-md text-on-surface">Lote</span>
              <Badge variant="warning">Pendiente</Badge>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2">
              {lote.mensaje_preview}
            </p>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              {lote.total_destinatarios} destinatario{lote.total_destinatarios !== 1 ? "s" : ""} — {lote.creado}
            </p>
          </div>
          <Button
            onClick={() => handleApprove(lote.id)}
            disabled={aprobarMutation.isPending}
            className="ml-md"
          >
            Aprobar
          </Button>
        </div>
      ))}
    </div>
  );
}
