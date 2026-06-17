import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { getCohortes, createCohorte, updateCohorte } from "../services/cohortes.service";
import AdminCohortesPage from "../pages/AdminCohortesPage";
import { CohorteFormModal } from "../components/CohorteFormModal";

describe("Cohortes Service", () => {
  it("getCohortes returns list", async () => {
    const res = await getCohortes();
    expect(res.status).toBe(200);
    expect(Array.isArray(res.data.items)).toBe(true);
    if (res.data.items.length > 0) {
      expect(res.data.items[0]).toHaveProperty("id");
      expect(res.data.items[0]).toHaveProperty("carrera_id");
      expect(res.data.items[0]).toHaveProperty("anio");
    }
  });

  it("getCohortes filters by carrera_id", async () => {
    const res = await getCohortes({ carrera_id: "carr-1" });
    expect(res.data.items.every((c) => c.carrera_id === "carr-1")).toBe(true);
  });

  it("createCohorte sends POST", async () => {
    const res = await createCohorte({
      nombre: "Test Cohorte",
      carrera_id: "carr-1",
      anio: 2024,
      vig_desde: "2024-03-01",
      vig_hasta: "2025-02-28",
    });
    expect(res.status).toBe(201);
    expect(res.data.nombre).toBe("Test Cohorte");
  });

  it("updateCohorte sends PUT", async () => {
    const res = await updateCohorte("coh-1", { nombre: "Updated Cohorte" });
    expect(res.data.nombre).toBe("Updated Cohorte");
  });
});

describe("CohorteFormModal", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
    cohorte: null,
  };

  it("renders create mode", () => {
    renderWithProviders(<CohorteFormModal {...defaultProps} />);
    expect(screen.getByText("Nuevo cohorte")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toHaveValue("");
  });

  it("renders edit mode", () => {
    renderWithProviders(
      <CohorteFormModal
        {...defaultProps}
        cohorte={{
          id: "coh-1",
          nombre: "Cohorte 2024",
          carrera_id: "carr-1",
          anio: 2024,
          vig_desde: "2024-03-01",
          vig_hasta: "2025-02-28",
          activo: true,
        }}
      />,
    );
    expect(screen.getByText("Editar cohorte")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre")).toHaveValue("Cohorte 2024");
  });

  it("shows validation errors for empty required fields", async () => {
    renderWithProviders(<CohorteFormModal {...defaultProps} />);
    screen.getByText("Crear").click();
    await waitFor(() => {
      expect(screen.getByText("El nombre es requerido")).toBeInTheDocument();
    });
  });
});

describe("AdminCohortesPage", () => {
  it("renders page header", () => {
    renderWithProviders(<AdminCohortesPage />);
    expect(screen.getByText("Cohortes")).toBeInTheDocument();
    expect(screen.getByText("Nuevo cohorte")).toBeInTheDocument();
  });

  it("renders table headers", async () => {
    renderWithProviders(<AdminCohortesPage />);
    await waitFor(() => {
      expect(screen.getByText("Nombre")).toBeInTheDocument();
    });
    expect(screen.getByText("Año")).toBeInTheDocument();
  });
});
