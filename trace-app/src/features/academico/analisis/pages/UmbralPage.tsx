import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useUmbral, useUmbralMutation } from "@/features/academico/analisis/hooks/useUmbral";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";

export default function UmbralPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { data, isLoading } = useUmbral(materiaId!, cohorteId!);
  const mutation = useUmbralMutation(materiaId!, cohorteId!);
  const [value, setValue] = useState(60);

  useEffect(() => {
    if (data?.umbral_pct != null) setValue(data.umbral_pct);
  }, [data?.umbral_pct]);

  const handleSave = useCallback(() => {
    mutation.mutate(value, {
      onSuccess: () => showToast("Umbral actualizado", "success"),
      onError: (err: Error) => showToast(err.message, "error"),
    });
  }, [mutation, value]);

  return (
    <div className="space-y-lg p-lg">
      <nav className="flex items-center gap-xs font-body-sm text-body-sm text-on-surface-variant">
        {breadcrumb.map((b, i) => (
          <span key={i} className="flex items-center gap-xs">
            {i > 0 && <span className="material-symbols-outlined text-[16px]">chevron_right</span>}
            {b.path ? (
              <a href={b.path} className="hover:text-primary transition-colors">{b.label}</a>
            ) : (
              <span className="text-on-surface">{b.label}</span>
            )}
          </span>
        ))}
      </nav>

      <Card className="mx-auto max-w-md p-xl">
        <h1 className="mb-lg font-headline-md text-headline-md text-on-surface">
          Umbral de aprobación
        </h1>

        {isLoading ? (
          <div className="space-y-md">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-8 w-24 mx-auto" />
          </div>
        ) : (
    <div className="space-y-lg p-lg">
            <div className="text-center">
              <span className="font-headline-lg text-headline-lg text-primary">{value}%</span>
            </div>

            <input
              type="range"
              min={0}
              max={100}
              value={value}
              onChange={(e) => setValue(Number(e.target.value))}
              className="w-full accent-primary"
            />

            <div className="flex justify-between font-body-sm text-body-sm text-on-surface-variant">
              <span>0%</span>
              <span>100%</span>
            </div>

            <Button
              onClick={handleSave}
              disabled={mutation.isPending || value === data?.umbral_pct}
              className="w-full"
            >
              {mutation.isPending ? "Guardando..." : "Guardar"}
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
