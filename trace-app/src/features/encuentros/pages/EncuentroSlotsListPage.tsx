import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSlotsList } from "@/features/encuentros/hooks/useEncuentrosSlots";
import { SlotCard } from "@/features/encuentros/components/SlotCard";
import { HtmlExportButton } from "@/features/encuentros/components/HtmlExportButton";
import { Skeleton } from "@/components/ui/Skeleton";

export default function EncuentroSlotsListPage() {
  const navigate = useNavigate();
  const [materiaId, setMateriaId] = useState("");

  const { data, isLoading } = useSlotsList(materiaId || undefined);
  const items = data?.items ?? [];

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Encuentros
        </h1>
        <div className="flex gap-2">
          <HtmlExportButton materiaId={materiaId} />
          <button
            onClick={() => navigate("/encuentros/crear")}
            className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Nuevo Slot
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Materia</label>
          <input
            type="text"
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            placeholder="ID de la materia"
            className="rounded-md border border-border bg-background px-3 py-2 text-sm w-64"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-on-surface-variant">
            {materiaId
              ? "No hay slots para esta materia"
              : "Seleccioná una materia para ver sus slots"}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((slot) => (
            <SlotCard key={slot.id} slot={slot} />
          ))}
        </div>
      )}
    </div>
  );
}
