import { useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

type UploadStepProps = {
  onUpload: (file: File) => void;
  isUploading: boolean;
  accept?: string;
  error?: string | null;
};

export function UploadStep({ onUpload, isUploading, accept = ".csv,.xlsx", error }: UploadStepProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [selected, setSelected] = useState<File | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setSelected(file);
  }

  function handleUpload() {
    if (selected) {
      onUpload(selected);
    }
  }

  return (
    <ErrorBoundary>
      <div className="flex flex-col items-center gap-md rounded-xl border-2 border-dashed border-outline-variant p-xl">
        <span className="material-symbols-outlined text-4xl text-secondary">cloud_upload</span>

        <p className="font-body-md text-body-md text-center text-on-surface-variant">
          Seleccioná un archivo CSV o Excel con las calificaciones para importar
        </p>

        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="hidden"
        />

        <Button
          type="button"
          variant="secondary"
          onClick={() => inputRef.current?.click()}
        >
          {selected ? selected.name : "Seleccionar archivo"}
        </Button>

        {selected && (
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            {selected.name} ({(selected.size / 1024).toFixed(1)} KB)
          </p>
        )}

        <Button onClick={handleUpload} disabled={!selected || isUploading} className="w-full max-w-xs">
          {isUploading ? "Subiendo..." : "Subir y previsualizar"}
        </Button>

        {error && (
          <p className="font-body-sm text-body-sm text-error" role="alert">
            {error}
          </p>
        )}
      </div>
    </ErrorBoundary>
  );
}
