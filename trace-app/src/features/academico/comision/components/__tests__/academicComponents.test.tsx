import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";

import { renderWithProviders } from "@/test/test-utils";
import { KpiCard } from "@/features/academico/comision/components/KpiCard";
import { AtrasadosTable } from "@/features/academico/analisis/components/AtrasadosTable";
import { ComunicarButton } from "@/features/academico/analisis/components/ComunicarButton";
import { UploadStep } from "@/features/academico/importacion/components/UploadStep";
import { TrackingTable } from "@/features/academico/comunicaciones/components/TrackingTable";
import type { AlumnoAtrasado, ComunicacionTrackingItem } from "@/api/types";

describe("KpiCard", () => {
  it("renders title and value", () => {
    renderWithProviders(<KpiCard title="Alumnos" icon="people" value={25} />);
    expect(screen.getByText("Alumnos")).toBeInTheDocument();
    expect(screen.getByText("25")).toBeInTheDocument();
  });

  it("shows skeleton when loading", () => {
    const { container } = renderWithProviders(
      <KpiCard title="Alumnos" icon="people" value={null} loading />,
    );
    const skeleton = container.querySelector(".animate-pulse");
    expect(skeleton).toBeInTheDocument();
  });

  it("shows fallback dash when value is null and not loading", () => {
    renderWithProviders(<KpiCard title="Alumnos" icon="people" value={null} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("shows fallback dash when value is 0", () => {
    renderWithProviders(<KpiCard title="Alumnos" icon="people" value={0} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });
});

describe("AtrasadosTable", () => {
  const alumnos: AlumnoAtrasado[] = [
    { entrada_padron_id: "a1", nombre: "Juan", apellidos: "Pérez", email: "juan@test.com", comision: "A", regional: "CABA", actividades_faltantes: ["TP1"], actividades_desaprobadas: ["Parcial"], total_actividades: 10, aprobadas: 3 },
    { entrada_padron_id: "a2", nombre: "María", apellidos: "García", email: "maria@test.com", comision: "B", regional: "GBA", actividades_faltantes: [], actividades_desaprobadas: ["TP1", "Parcial"], total_actividades: 10, aprobadas: 4 },
  ];

  it("renders student rows", () => {
    renderWithProviders(<AtrasadosTable alumnos={alumnos} selectedIds={[]} onToggle={() => {}} />);
    expect(screen.getByText("Juan Pérez")).toBeInTheDocument();
    expect(screen.getByText("María García")).toBeInTheDocument();
  });

  it("shows empty state when no alumnos", () => {
    renderWithProviders(<AtrasadosTable alumnos={[]} selectedIds={[]} onToggle={() => {}} />);
    expect(screen.getByText("No hay alumnos atrasados")).toBeInTheDocument();
  });

  it("renders status badges", () => {
    renderWithProviders(<AtrasadosTable alumnos={alumnos} selectedIds={[]} onToggle={() => {}} />);
    expect(screen.getAllByText("TP1").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Parcial").length).toBeGreaterThanOrEqual(1);
  });
});

describe("ComunicarButton", () => {
  it("is disabled when no alumnos selected", () => {
    renderWithProviders(<ComunicarButton selectedIds={[]} />, {
      initialEntries: ["/academico/m1/c1/atrasados"],
    });
    const btn = screen.getByRole("button");
    expect(btn).toBeDisabled();
    expect(btn).toHaveTextContent("Comunicar (0)");
  });

  it("is enabled with selected count", () => {
    renderWithProviders(<ComunicarButton selectedIds={["a1", "a2"]} />, {
      initialEntries: ["/academico/m1/c1/atrasados"],
    });
    const btn = screen.getByRole("button");
    expect(btn).not.toBeDisabled();
    expect(btn).toHaveTextContent("Comunicar (2)");
  });
});

describe("UploadStep", () => {
  it("renders upload UI", () => {
    renderWithProviders(<UploadStep onUpload={() => {}} isUploading={false} />);
    expect(screen.getByText("Seleccionar archivo")).toBeInTheDocument();
    expect(screen.getByText("Subir y previsualizar")).toBeInTheDocument();
  });

  it("disables upload button when uploading", () => {
    renderWithProviders(<UploadStep onUpload={() => {}} isUploading={true} />);
    const btn = screen.getByText("Subiendo...");
    expect(btn).toBeDisabled();
  });
});

describe("TrackingTable", () => {
  const items: ComunicacionTrackingItem[] = [
    { id: "c1", alumno_id: "a1", nombre: "Juan", apellido: "Pérez", estado: "enviado", timestamp: "2024-01-01" },
    { id: "c2", alumno_id: "a2", nombre: "María", apellido: "García", estado: "pendiente", timestamp: "2024-01-01" },
    { id: "c3", alumno_id: "a3", nombre: "Pedro", apellido: "López", estado: "error", timestamp: "2024-01-01", error_mensaje: "Error de envío" },
  ];

  it("renders all tracking items", () => {
    renderWithProviders(<TrackingTable items={items} onCancel={() => {}} />);
    expect(screen.getByText("Juan Pérez")).toBeInTheDocument();
    expect(screen.getByText("María García")).toBeInTheDocument();
    expect(screen.getByText("Pedro López")).toBeInTheDocument();
  });

  it("shows status badges with correct labels", () => {
    renderWithProviders(<TrackingTable items={items} onCancel={() => {}} />);
    expect(screen.getByText("Enviado")).toBeInTheDocument();
    expect(screen.getByText("Pendiente")).toBeInTheDocument();
    expect(screen.getAllByText("Error")).toHaveLength(2);
  });

  it("shows cancel button only for pending items", () => {
    renderWithProviders(<TrackingTable items={items} onCancel={() => {}} />);
    const cancelButtons = screen.getAllByText("Cancelar");
    expect(cancelButtons).toHaveLength(1);
  });
});
