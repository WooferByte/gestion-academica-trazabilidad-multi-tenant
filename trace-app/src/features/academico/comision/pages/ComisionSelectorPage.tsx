import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useComisionSelector } from "@/features/academico/hooks/useComisionSelector";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

export default function ComisionSelectorPage() {
  const navigate = useNavigate();
  const { query, materiasUnicas, getCohortes } = useComisionSelector();
  const [selectedMateria, setSelectedMateria] = useState("");
  const [selectedCohorte, setSelectedCohorte] = useState("");

  const cohortes = selectedMateria ? getCohortes(selectedMateria) : [];

  function handleSubmit() {
    if (selectedMateria && selectedCohorte) {
      navigate(`/academico/${selectedMateria}/${selectedCohorte}`);
    }
  }

  if (query.isLoading) {
    return (
      <div className="mx-auto mt-xl max-w-lg space-y-md">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }

  if (query.error) {
    return (
      <div className="mx-auto mt-xl max-w-lg text-center">
        <p className="font-body-lg text-body-lg text-error">Error al cargar comisiones</p>
        <Button variant="secondary" onClick={() => query.refetch()} className="mt-md">
          Reintentar
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto mt-xl max-w-lg">
      <Card className="p-xl">
        <h1 className="mb-lg font-headline-md text-headline-md text-on-surface">
          Seleccionar Comisión
        </h1>

        <div className="space-y-md">
          <div>
            <label className="mb-xs block font-label-md text-label-md text-on-surface-variant">
              Materia
            </label>
            <select
              value={selectedMateria}
              onChange={(e) => {
                setSelectedMateria(e.target.value);
                setSelectedCohorte("");
              }}
              className="w-full rounded-lg border border-outline-variant bg-white px-md py-sm font-body-md text-body-md text-on-surface"
            >
              <option value="">Seleccionar materia...</option>
              {materiasUnicas.map((m) => (
                <option key={m.materia_id} value={m.materia_id}>
                  {m.materia_nombre}
                </option>
              ))}
            </select>
          </div>

          {selectedMateria && (
            <div>
              <label className="mb-xs block font-label-md text-label-md text-on-surface-variant">
                Cohorte
              </label>
              <select
                value={selectedCohorte}
                onChange={(e) => setSelectedCohorte(e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-white px-md py-sm font-body-md text-body-md text-on-surface"
              >
                <option value="">Seleccionar cohorte...</option>
                {cohortes.map((c) => (
                  <option key={c.cohorte_id} value={c.cohorte_id}>
                    {c.cohorte_nombre}
                  </option>
                ))}
              </select>
            </div>
          )}

          <Button
            onClick={handleSubmit}
            disabled={!selectedMateria || !selectedCohorte}
            className="w-full"
          >
            Ir al panel
          </Button>
        </div>
      </Card>
    </div>
  );
}
