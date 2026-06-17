import { useState } from "react";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useCerrarLiquidacion } from "../hooks/useLiquidaciones";

type CerrarLiquidacionDialogProps = {
  open: boolean;
  onClose: () => void;
};

export function CerrarLiquidacionDialog({ open, onClose }: CerrarLiquidacionDialogProps) {
  const [cohorteId, setCohorteId] = useState("");
  const [periodo, setPeriodo] = useState("");
  const cerrarMutation = useCerrarLiquidacion();

  const handleConfirm = async () => {
    if (!cohorteId || !periodo) return;
    await cerrarMutation.mutateAsync({ cohorteId, periodo });
    setCohorteId("");
    setPeriodo("");
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="Cerrar Liquidaciones"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="danger"
            onClick={handleConfirm}
            disabled={!cohorteId || !periodo || cerrarMutation.isPending}
          >
            {cerrarMutation.isPending ? "Cerrando..." : "Cerrar"}
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-md">
        <p className="text-body-md text-on-surface-variant">
          Esta acción cerrará las liquidaciones del período indicado y no se puede deshacer.
        </p>
        <Input
          label="Cohorte ID"
          value={cohorteId}
          onChange={(e) => setCohorteId(e.target.value)}
          placeholder="ID de la cohorte"
        />
        <Input
          label="Período"
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          placeholder="Ej: 2025-01"
        />
      </div>
    </Dialog>
  );
}
