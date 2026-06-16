import { useAvisosActivos } from "@/features/avisos/hooks/useAvisosActivos";
import { useConfirmarLectura } from "@/features/avisos/hooks/useConfirmarLectura";
import { AvisoCard } from "@/features/avisos/components/AvisoCard";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";

export default function AvisosActivosPage() {
  const { data, isLoading } = useAvisosActivos(30000);
  const ackMutation = useConfirmarLectura();

  const items = data?.items ?? [];

  const handleAck = (avisoId: string) => {
    ackMutation.mutate(avisoId, {
      onSuccess: () => showToast("Lectura confirmada", "success"),
      onError: () => showToast("Error al confirmar lectura", "error"),
    });
  };

  return (
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Avisos Activos
      </h1>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-8 text-on-surface-variant">
          No hay avisos activos para vos
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((aviso) => (
            <AvisoCard
              key={aviso.id}
              aviso={aviso}
              onAck={handleAck}
              isPending={ackMutation.isPending}
            />
          ))}
        </div>
      )}
    </div>
  );
}
