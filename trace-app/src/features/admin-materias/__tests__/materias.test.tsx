import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { getMaterias, createMateria } from "../services/materias.service";
import AdminMateriasPage from "../pages/AdminMateriasPage";
import { MateriaFormModal } from "../components/MateriaFormModal";

describe("Materias Service", () => {
  it("getMaterias returns list", async () => {
    const res = await getMaterias();
    expect(res.status).toBe(200);
    expect(Array.isArray(res.data.items)).toBe(true);
    if (res.data.items.length > 0) {
      expect(res.data.items[0]).toHaveProperty("id");
      expect(res.data.items[0]).toHaveProperty("codigo");
      expect(res.data.items[0]).toHaveProperty("nombre");
    }
  });

  it("getMaterias filters by activo", async () => {
    const res = await getMaterias({ activo: true });
    expect(res.data.items.every((m) => m.estado === "Activa")).toBe(true);
  });

  it("createMateria sends POST", async () => {
    const res = await createMateria({ codigo: "NEW-001", nombre: "Nueva Materia" });
    expect(res.status).toBe(201);
    expect(res.data.codigo).toBe("NEW-001");
  });

  it("createMateria rejects duplicate codigo", async () => {
    try {
      await createMateria({ codigo: "MAT-101", nombre: "Duplicate" });
      expect.fail("Should have thrown");
    } catch (error: unknown) {
      const axiosError = error as { response?: { status?: number } };
      expect(axiosError.response?.status).toBe(409);
    }
  });
});

describe("MateriaFormModal", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
    materia: null,
  };

  it("renders create mode", () => {
    renderWithProviders(<MateriaFormModal {...defaultProps} />);
    expect(screen.getByText("Nueva materia")).toBeInTheDocument();
  });

  it("renders edit mode with pre-filled values", () => {
    renderWithProviders(
      <MateriaFormModal
        {...defaultProps}
        materia={{ id: "mat-101", codigo: "MAT-101", nombre: "Matemática I", activo: true }}
      />,
    );
    expect(screen.getByText("Editar materia")).toBeInTheDocument();
    expect(screen.getByLabelText("Código")).toHaveValue("MAT-101");
  });

  it("shows validation errors for empty required fields", async () => {
    renderWithProviders(<MateriaFormModal {...defaultProps} />);
    screen.getByText("Crear").click();
    await waitFor(() => {
      expect(screen.getByText("El código es requerido")).toBeInTheDocument();
      expect(screen.getByText("El nombre es requerido")).toBeInTheDocument();
    });
  });
});

describe("AdminMateriasPage", () => {
  it("renders page header", () => {
    renderWithProviders(<AdminMateriasPage />);
    expect(screen.getByText("Materias")).toBeInTheDocument();
    expect(screen.getByText("Nueva materia")).toBeInTheDocument();
  });

  it("renders table headers", async () => {
    renderWithProviders(<AdminMateriasPage />);
    await waitFor(() => {
      expect(screen.getByText("Código")).toBeInTheDocument();
    });
    expect(screen.getByText("Nombre")).toBeInTheDocument();
    expect(screen.getByText("Estado")).toBeInTheDocument();
  });
});
