import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";

type CambiarEstadoFacturaButtonProps = {
  estadoActual: string;
  facturaId: string;
  onChangeEstado: (id: string, nuevoEstado: string) => void;
  isPending: boolean;
};

export function CambiarEstadoFacturaButton({
  estadoActual,
  facturaId,
  onChangeEstado,
  isPending,
}: CambiarEstadoFacturaButtonProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  // Backend solo permite cambiar de Pendiente a Abonada (no permite revertir)
  if (estadoActual?.toLowerCase() === "abonada") {
    return <span className="text-sm text-green-600 font-medium">Abonada</span>;
  }

  const handleConfirm = () => {
    onChangeEstado(facturaId, "Abonada");
    setShowConfirm(false);
  };

  return (
    <>
      <Button
        variant="primary"
        size="sm"
        onClick={() => setShowConfirm(true)}
        disabled={isPending}
      >
        {isPending ? "Guardando..." : "Marcar como abonada"}
      </Button>
      <ConfirmDialog
        open={showConfirm}
        onConfirm={handleConfirm}
        onCancel={() => setShowConfirm(false)}
        title="Cambiar estado de factura"
        message="¿Estás seguro de marcar esta factura como abonada?"
        confirmLabel="Confirmar"
      />
    </>
  );
}
