import type { AvisoResponse } from "@/api/types";

interface AvisoCardProps {
  aviso: AvisoResponse;
  onAck?: (avisoId: string) => void;
  isPending?: boolean;
}

const severityStyles: Record<string, string> = {
  Info: "border-blue-200 bg-blue-50",
  Advertencia: "border-yellow-200 bg-yellow-50",
  Urgente: "border-red-200 bg-red-50",
};

const severityBadge: Record<string, string> = {
  Info: "bg-blue-100 text-blue-800",
  Advertencia: "bg-yellow-100 text-yellow-800",
  Urgente: "bg-red-100 text-red-800",
};

export function AvisoCard({ aviso, onAck, isPending }: AvisoCardProps) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        severityStyles[aviso.severidad] ?? "border-border bg-surface"
      } ${!aviso.user_acked && aviso.requiere_ack ? "ring-2 ring-primary/20" : ""}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-sm truncate">{aviso.titulo}</h3>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                severityBadge[aviso.severidad] ?? "bg-gray-100 text-gray-800"
              }`}
            >
              {aviso.severidad}
            </span>
          </div>
          <p className="text-sm text-on-surface-variant whitespace-pre-line">
            {aviso.cuerpo}
          </p>
          <p className="text-xs text-on-surface-variant mt-2">
            {new Date(aviso.inicio_vigencia).toLocaleDateString()} —{" "}
            {new Date(aviso.fin_vigencia).toLocaleDateString()}
          </p>
        </div>

        {aviso.requiere_ack && !aviso.user_acked && onAck && (
          <button
            onClick={() => onAck(aviso.id)}
            disabled={isPending}
            className="shrink-0 px-3 py-1.5 text-xs rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isPending ? "Confirmando..." : "Confirmar lectura"}
          </button>
        )}

        {aviso.user_acked && (
          <span className="shrink-0 text-xs text-green-600 font-medium">
            ✓ Leído
          </span>
        )}
      </div>
    </div>
  );
}
