import { useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import type { ComunicacionTrackingItem } from "@/api/types";

type TrackingTableProps = {
  items: ComunicacionTrackingItem[];
  onCancel: (id: string) => void;
};

const STATUS_CONFIG = {
  pendiente: { label: "Pendiente", variant: "warning" as const },
  enviando: { label: "Enviando", variant: "info" as const },
  enviado: { label: "Enviado", variant: "success" as const },
  error: { label: "Error", variant: "error" as const },
  cancelado: { label: "Cancelado", variant: "default" as const },
};

export function TrackingTable({ items, onCancel }: TrackingTableProps) {
  const [cancelTarget, setCancelTarget] = useState<string | null>(null);

  return (
    <>
      <div className="overflow-x-auto rounded-xl border border-outline-variant bg-white">
        <table className="w-full text-left font-body-md text-body-md">
          <thead>
            <tr className="border-b border-outline-variant text-label-sm text-on-surface-variant">
              <th className="py-sm px-md">Nombre</th>
              <th className="py-sm pr-md">Estado</th>
              <th className="py-sm pr-md">Fecha</th>
              <th className="py-sm">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const cfg = STATUS_CONFIG[item.estado];
              return (
                <tr
                  key={item.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                >
                  <td className="py-sm px-md font-medium text-on-surface">
                    {item.nombre} {item.apellido}
                  </td>
                  <td className="py-sm pr-md">
                    <Badge variant={cfg.variant}>{cfg.label}</Badge>
                  </td>
                  <td className="py-sm pr-md text-on-surface-variant">{item.timestamp}</td>
                  <td className="py-sm">
                    {item.estado === "pendiente" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setCancelTarget(item.id)}
                      >
                        Cancelar
                      </Button>
                    )}
                    {item.estado === "error" && item.error_mensaje && (
                      <span className="font-body-sm text-body-sm text-error" title={item.error_mensaje}>
                        Error
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Dialog
        open={!!cancelTarget}
        onClose={() => setCancelTarget(null)}
        title="Cancelar comunicación"
        footer={
          <>
            <Button variant="ghost" onClick={() => setCancelTarget(null)}>Volver</Button>
            <Button
              variant="danger"
              onClick={() => {
                if (cancelTarget) {
                  onCancel(cancelTarget);
                  setCancelTarget(null);
                }
              }}
            >
              Cancelar comunicación
            </Button>
          </>
        }
      >
        <p className="font-body-md text-body-md text-on-surface">
          ¿Estás seguro de que querés cancelar esta comunicación?
        </p>
      </Dialog>
    </>
  );
}
