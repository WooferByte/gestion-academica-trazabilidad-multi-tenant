import { useState } from "react";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useCalcularLiquidacion } from "../hooks/useLiquidaciones";

type CalcularLiquidacionDialogProps = {
  open: boolean;
  onClose: () => void;
};

export function CalcularLiquidacionDialog({ open, onClose }: CalcularLiquidacionDialogProps) {
  const [cohorteId, setCohorteId] = useState("");
  const [periodo, setPeriodo] = useState("");
  const calcularMutation = useCalcularLiquidacion();

  const handleSubmit = async () => {
    if (!cohorteId || !periodo) return;
    await calcularMutation.mutateAsync({ cohorte_id: cohorteId, periodo });
    setCohorteId("");
    setPeriodo("");
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="Calcular Liquidaciones"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!cohorteId || !periodo || calcularMutation.isPending}
          >
            {calcularMutation.isPending ? "Calculando..." : "Calcular"}
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-md">
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
