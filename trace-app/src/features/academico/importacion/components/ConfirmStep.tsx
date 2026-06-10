import { Button } from "@/components/ui/Button";

type ConfirmStepProps = {
  importedCount: number | null;
  isSuccess: boolean;
  isError: boolean;
  errorMessage: string | null;
  onFinish: () => void;
  onRetry: () => void;
};

export function ConfirmStep({
  importedCount,
  isSuccess,
  isError,
  errorMessage,
  onFinish,
  onRetry,
}: ConfirmStepProps) {
  if (isError) {
    return (
      <div className="flex flex-col items-center gap-md rounded-xl border border-outline-variant p-xl text-center">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <p className="font-body-lg text-body-lg text-error">Error al importar</p>
        <p className="font-body-sm text-body-sm text-on-surface-variant">{errorMessage}</p>
        <Button variant="secondary" onClick={onRetry}>Reintentar</Button>
      </div>
    );
  }

  if (isSuccess) {
    return (
      <div className="flex flex-col items-center gap-md rounded-xl border border-outline-variant p-xl text-center">
        <span className="material-symbols-outlined text-4xl text-green-600">check_circle</span>
        <p className="font-headline-sm text-headline-sm text-on-surface">Importación completada</p>
        <p className="font-body-md text-body-md text-on-surface-variant">
          {importedCount != null
            ? `Se importaron ${importedCount} registros correctamente.`
            : "Datos importados correctamente."}
        </p>
        <Button onClick={onFinish}>Finalizar</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-md p-xl">
      <span className="material-symbols-outlined animate-spin text-4xl text-secondary">
        progress_activity
      </span>
      <p className="font-body-md text-body-md text-on-surface-variant">Importando...</p>
    </div>
  );
}
