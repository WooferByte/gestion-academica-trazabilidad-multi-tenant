import { useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useFileUpload } from "@/features/academico/importacion/hooks/useFileUpload";
import {
  useImportarPreview,
  useImportarConfirmar,
  useImportarFinalizacion,
} from "@/features/academico/importacion/hooks/useImportarCalificaciones";
import {
  usePadronPreview,
  usePadronConfirmar,
} from "@/features/academico/importacion/hooks/useImportarPadron";
import { useVaciarMateria } from "@/features/academico/importacion/hooks/useVaciarMateria";
import { ImportTabs } from "@/features/academico/importacion/components/ImportTabs";
import { UploadStep } from "@/features/academico/importacion/components/UploadStep";
import { PreviewStep } from "@/features/academico/importacion/components/PreviewStep";
import { ConfirmStep } from "@/features/academico/importacion/components/ConfirmStep";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import type { CalificacionesPreviewResponse, PadronPreviewResponse } from "@/api/types";

const TABS = [
  { id: "padron", label: "1. Padrón" },
  { id: "calificaciones", label: "2. Calificaciones" },
  { id: "finalizacion", label: "3. Finalización" },
];

type WizardStep = "upload" | "preview" | "confirm";

export default function ImportarPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const [activeTab, setActiveTab] = useState("padron");
  const [wizardStep, setWizardStep] = useState<WizardStep>("upload");
  const [selectedActividades, setSelectedActividades] = useState<string[]>([]);
  const [previewData, setPreviewData] = useState<CalificacionesPreviewResponse | null>(null);
  const [padronPreview, setPadronPreview] = useState<PadronPreviewResponse | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [finalizacionResult, setFinalizacionResult] = useState<{ total: number } | null>(null);
  const [showVaciarDialog, setShowVaciarDialog] = useState(false);

  const uploadState = useFileUpload();

  const previewMutation = useImportarPreview();
  const confirmMutation = useImportarConfirmar();
  const finalizacionMutation = useImportarFinalizacion();
  const padronPreviewMutation = usePadronPreview();
  const padronConfirmMutation = usePadronConfirmar();
  const vaciarMutation = useVaciarMateria();

  const handleUpload = useCallback((file: File) => {
    setUploadedFile(file);
    uploadState.reset();
    uploadState.setState("uploading");

    function handleError(err: unknown) {
      let msg = "Error al procesar el archivo";
      try {
        const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
        const detail = axiosErr?.response?.data?.detail;
        if (Array.isArray(detail)) {
          msg = detail.map((d: { msg?: string }) => d.msg ?? "").filter(Boolean).join("; ");
        } else if (typeof detail === "string") {
          msg = detail;
        } else if (axiosErr?.message) {
          msg = axiosErr.message;
        }
      } catch {
        // ignore parse errors
      }
      uploadState.setError(msg);
      uploadState.setState("error");
    }

    if (activeTab === "calificaciones") {
      const fd = new FormData();
      fd.append("archivo", file);
      fd.append("materia_id", materiaId!);
      fd.append("cohorte_id", cohorteId!);

      previewMutation.mutate(fd, {
        onSuccess: (data) => {
          setPreviewData(data);
          const ids = data.actividades.map((a) => a.id);
          if (new Set(ids).size !== ids.length) {
            console.warn("IDs duplicados en actividades:", ids);
          }
          setSelectedActividades(data.actividades.map((a) => a.nombre));
          uploadState.setFileToken(data.file_token);
          uploadState.setState("preview");
          setWizardStep("preview");
        },
        onError: handleError,
      });
    } else if (activeTab === "padron") {
      const fd = new FormData();
      fd.append("archivo", file);
      fd.append("materia_id", materiaId!);
      fd.append("cohorte_id", cohorteId!);

      padronPreviewMutation.mutate(fd, {
        onSuccess: (data) => {
          setPadronPreview(data);
          uploadState.setFileToken(null);
          uploadState.setState("preview");
          setWizardStep("preview");
        },
        onError: handleError,
      });
    }
  }, [activeTab, materiaId, cohorteId, uploadState, previewMutation, padronPreviewMutation]);

  const handleConfirm = useCallback(() => {
    uploadState.setState("confirming");

    if (activeTab === "calificaciones" && previewData && uploadedFile) {
      const fd = new FormData();
      fd.append("archivo", uploadedFile);
      fd.append("materia_id", materiaId!);
      fd.append("cohorte_id", cohorteId!);
      const actividadesToSend = previewData.actividades
        .filter((a) => selectedActividades.includes(a.nombre))
        .map((a) => ({ nombre: a.nombre, tipo: a.tipo }));
      fd.append("actividades", JSON.stringify(actividadesToSend));

      confirmMutation.mutate(fd, {
        onSuccess: (data) => {
          uploadState.setState("done");
          setWizardStep("confirm");
          showToast(`Importación exitosa: ${data.calificaciones_creadas} calificaciones`, "success");
        },
        onError: (err: unknown) => {
          let msg = "Error al confirmar importación";
          try {
            const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
            const detail = axiosErr?.response?.data?.detail;
            if (Array.isArray(detail)) {
              msg = detail.map((d: { msg?: string }) => d.msg ?? "").filter(Boolean).join("; ");
            } else if (typeof detail === "string") {
              msg = detail;
            } else if (axiosErr?.message) {
              msg = axiosErr.message;
            }
          } catch { /* ignore */ }
          uploadState.setError(msg);
          uploadState.setState("error");
        },
      });
    } else if (activeTab === "padron" && padronPreview && uploadedFile) {
      const fd = new FormData();
      fd.append("archivo", uploadedFile);
      fd.append("materia_id", materiaId!);
      fd.append("cohorte_id", cohorteId!);

      padronConfirmMutation.mutate(fd, {
        onSuccess: (data) => {
          uploadState.setState("done");
          setWizardStep("confirm");
          showToast(`Padrón importado correctamente`, "success");
        },
        onError: (err: unknown) => {
          let msg = "Error al importar padrón";
          try {
            const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
            const detail = axiosErr?.response?.data?.detail;
            if (Array.isArray(detail)) {
              msg = detail.map((d: { msg?: string }) => d.msg ?? "").filter(Boolean).join("; ");
            } else if (typeof detail === "string") {
              msg = detail;
            } else if (axiosErr?.message) {
              msg = axiosErr.message;
            }
          } catch { /* ignore */ }
          uploadState.setError(msg);
          uploadState.setState("error");
        },
      });
    }
  }, [activeTab, previewData, padronPreview, selectedActividades, uploadedFile, materiaId, cohorteId, uploadState, confirmMutation, padronConfirmMutation]);

  const handleFinalizacionUpload = useCallback((file: File) => {
    uploadState.setState("uploading");
    const fd = new FormData();
    fd.append("archivo", file);
    fd.append("materia_id", materiaId!);
    fd.append("cohorte_id", cohorteId!);

    finalizacionMutation.mutate(fd, {
      onSuccess: (data) => {
        setFinalizacionResult(data);
        setWizardStep("confirm");
        uploadState.setState("done");
      },
      onError: (err: unknown) => {
        let msg = "Error al procesar finalización";
        try {
          const axiosErr = err as { response?: { data?: { detail?: unknown } }; message?: string };
          const detail = axiosErr?.response?.data?.detail;
          if (Array.isArray(detail)) {
            msg = detail.map((d: { msg?: string }) => d.msg ?? "").filter(Boolean).join("; ");
          } else if (typeof detail === "string") {
            msg = detail;
          } else if (axiosErr?.message) {
            msg = axiosErr.message;
          }
        } catch { /* ignore */ }
        showToast(msg, "error");
      },
    });
  }, [materiaId, cohorteId, uploadState, finalizacionMutation]);

  const handleVaciar = useCallback(() => {
    vaciarMutation.mutate(
      { materiaId: materiaId!, cohorteId: cohorteId! },
      {
        onSuccess: () => {
          showToast("Datos de materia eliminados", "success");
          setShowVaciarDialog(false);
        },
        onError: (err: Error) => {
          showToast(err.message, "error");
        },
      },
    );
  }, [materiaId, cohorteId, vaciarMutation]);

  const handleToggle = useCallback((id: string) => {
    setSelectedActividades((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }, []);

  const handleBack = useCallback(() => {
    setWizardStep("upload");
    uploadState.reset();
    setPreviewData(null);
    setPadronPreview(null);
  }, [uploadState]);

  const handleFinish = useCallback(() => {
    setWizardStep("upload");
    uploadState.reset();
    setPreviewData(null);
    setPadronPreview(null);
  }, [uploadState]);

  if (!materiaId || !cohorteId) {
    return (
      <div className="flex flex-col items-center gap-md p-xl text-center">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <h1 className="font-headline-md text-headline-md text-on-surface">Error</h1>
        <p className="font-body-md text-body-md text-secondary">No se encontró la comisión seleccionada.</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-lg text-headline-lg text-on-surface">Importar</h1>

      <ImportTabs tabs={TABS} active={activeTab} onChange={(id) => { setActiveTab(id); handleFinish(); }} />

      <div className="rounded-xl border border-outline-variant bg-white p-lg">
        {wizardStep === "upload" && (
          <>
            {activeTab === "finalizacion" ? (
              <div className="space-y-md">
                <UploadStep
                  onUpload={handleFinalizacionUpload}
                  isUploading={finalizacionMutation.isPending}
                  error={uploadState.error}
                />
                <div className="pt-md">
                  <Button
                    variant="danger"
                    onClick={() => setShowVaciarDialog(true)}
                  >
                    Vaciar datos de materia
                  </Button>
                </div>
                <details className="rounded-lg border border-outline-variant px-md py-sm text-body-sm text-on-surface-variant">
                  <summary className="cursor-pointer font-label-md text-label-md">Formato del CSV</summary>
                  <ul className="mt-sm list-disc pl-md space-y-xs">
                    <li>Columnas: <code>nombre, apellido, email, legajo, comision, Actividad1(Real), Actividad2(Real), ...</code></li>
                    <li>Las actividades con <code>(Real)</code> se detectan como numéricas</li>
                    <li>Para marcar entregas sin corregir, usá <code>entregado</code> en las actividades textuales</li>
                  </ul>
                </details>
              </div>
            ) : activeTab === "padron" ? (
              <div className="space-y-md">
                <UploadStep
                  onUpload={handleUpload}
                  isUploading={padronPreviewMutation.isPending}
                  error={uploadState.error}
                />
                <details className="rounded-lg border border-outline-variant px-md py-sm text-body-sm text-on-surface-variant">
                  <summary className="cursor-pointer font-label-md text-label-md">Formato del CSV</summary>
                  <ul className="mt-sm list-disc pl-md space-y-xs">
                    <li>Columnas requeridas: <code>nombre, apellidos, email, comision, regional</code></li>
                    <li>Podés incluir columnas adicionales (ej: <code>legajo</code>) que se ignoran</li>
                    <li>Cada fila representa un alumno a importar en el padrón</li>
                  </ul>
                </details>
              </div>
            ) : (
              <div className="space-y-md">
                <UploadStep
                  onUpload={handleUpload}
                  isUploading={previewMutation.isPending}
                  error={uploadState.error}
                />
                <details className="rounded-lg border border-outline-variant px-md py-sm text-body-sm text-on-surface-variant">
                  <summary className="cursor-pointer font-label-md text-label-md">Formato del CSV</summary>
                  <ul className="mt-sm list-disc pl-md space-y-xs">
                    <li>Columnas: <code>nombre, apellido, email, legajo, comision, Actividad1, Actividad2, ...</code></li>
                    <li>Cada columna que no sea de identificación se detecta como actividad</li>
                    <li>Las notas se vinculan con los alumnos del padrón por <code>nombre + apellido + email</code></li>
                  </ul>
                </details>
              </div>
            )}
          </>
        )}

        {wizardStep === "preview" && activeTab === "calificaciones" && previewData && (
          <PreviewStep
            actividades={previewData.actividades}
            selectedIds={selectedActividades}
            onToggle={handleToggle}
            isConfirming={confirmMutation.isPending}
            onConfirm={handleConfirm}
            onBack={handleBack}
            error={uploadState.error}
          />
        )}

        {wizardStep === "preview" && activeTab === "padron" && padronPreview && (
          <div className="space-y-md">
            <h3 className="font-label-lg text-label-lg text-on-surface">
              Alumnos detectados ({padronPreview.total})
            </h3>
            <div className="max-h-64 overflow-y-auto">
              <table className="w-full text-left font-body-sm text-body-sm">
                <thead>
                  <tr className="border-b border-outline-variant text-on-surface-variant">
                    <th className="py-sm pr-md">Nombre</th>
                    <th className="py-sm pr-md">Email</th>
                    <th className="py-sm pr-md">Comisión</th>
                    <th className="py-sm">Regional</th>
                  </tr>
                </thead>
                <tbody>
                  {padronPreview.items.map((a, i) => (
                    <tr key={i} className="border-b border-outline-variant last:border-0">
                      <td className="py-sm pr-md">{a.nombre} {a.apellidos}</td>
                      <td className="py-sm pr-md">{a.email}</td>
                      <td className="py-sm pr-md">{a.comision}</td>
                      <td className="py-sm">{a.regional}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between">
              <Button variant="ghost" onClick={handleBack}>Volver</Button>
              <Button onClick={handleConfirm} disabled={padronConfirmMutation.isPending}>
                {padronConfirmMutation.isPending ? "Importando..." : "Confirmar importación"}
              </Button>
            </div>
          </div>
        )}

        {wizardStep === "confirm" && finalizacionResult && (
          <div className="flex flex-col items-center gap-md rounded-xl border border-outline-variant p-xl text-center">
            <span className="material-symbols-outlined text-4xl text-green-600">check_circle</span>
            <p className="font-headline-sm text-headline-sm text-on-surface">Importación completada</p>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {finalizacionResult.total > 0
                ? `Hay ${finalizacionResult.total} entregas sin corregir`
                : "Hay 0 entregas sin corregir"}
            </p>
            <Button onClick={handleFinish}>Finalizar</Button>
          </div>
        )}

        {wizardStep === "confirm" && !finalizacionResult && (
          <ConfirmStep
            importedCount={confirmMutation.data?.calificaciones_creadas ?? null}
            isSuccess={confirmMutation.isSuccess || padronConfirmMutation.isSuccess}
            isError={uploadState.state === "error"}
            errorMessage={uploadState.error}
            onFinish={handleFinish}
            onRetry={handleBack}
          />
        )}
      </div>

      <Dialog
        open={showVaciarDialog}
        onClose={() => setShowVaciarDialog(false)}
        title="Vaciar datos de materia"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowVaciarDialog(false)}>Cancelar</Button>
            <Button variant="danger" onClick={handleVaciar} disabled={vaciarMutation.isPending}>
              {vaciarMutation.isPending ? "Vaciando..." : "Confirmar vaciado"}
            </Button>
          </>
        }
      >
        <p className="font-body-md text-body-md text-on-surface">
          ¿Estás seguro de que querés eliminar todos los datos de esta materia? Esta acción no se puede deshacer.
        </p>
      </Dialog>
    </div>
    </ErrorBoundary>
  );
}
