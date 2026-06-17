import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { getCarreras, createCarrera, updateCarrera, deleteCarrera } from "../services/carreras.service";
import AdminCarrerasPage from "../pages/AdminCarrerasPage";
import { CarreraFormModal } from "../components/CarreraFormModal";

describe("Carreras Service", () => {
  it("getCarreras returns list", async () => {
    const res = await getCarreras();
    expect(res.status).toBe(200);
    expect(Array.isArray(res.data.items)).toBe(true);
    if (res.data.items.length > 0) {
      expect(res.data.items[0]).toHaveProperty("id");
      expect(res.data.items[0]).toHaveProperty("codigo");
      expect(res.data.items[0]).toHaveProperty("nombre");
    }
  });

  it("getCarreras filters by activo", async () => {
    const res = await getCarreras({ activo: true });
    expect(res.data.items.every((c) => c.estado === "Activa")).toBe(true);
  });

  it("createCarrera sends POST", async () => {
    const res = await createCarrera({ codigo: "TEST-01", nombre: "Test" });
    expect(res.status).toBe(201);
    expect(res.data.codigo).toBe("TEST-01");
  });

  it("updateCarrera sends PUT", async () => {
    const res = await updateCarrera("carr-1", { nombre: "Updated" });
    expect(res.data.nombre).toBe("Updated");
  });

  it("deleteCarrera sends DELETE", async () => {
    const res = await deleteCarrera("carr-3");
    expect(res.status).toBe(204);
  });
});

describe("CarreraFormModal", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
    carrera: null,
  };

  it("renders create mode with empty fields", () => {
    renderWithProviders(<CarreraFormModal {...defaultProps} />);
    expect(screen.getByText("Nueva carrera")).toBeInTheDocument();
    expect(screen.getByLabelText("Código")).toHaveValue("");
    expect(screen.getByLabelText("Nombre")).toHaveValue("");
  });

  it("renders edit mode with pre-filled values", () => {
    renderWithProviders(
      <CarreraFormModal
        {...defaultProps}
        carrera={{ id: "carr-1", codigo: "ING-2024", nombre: "Ingeniería", activo: true }}
      />,
    );
    expect(screen.getByText("Editar carrera")).toBeInTheDocument();
    expect(screen.getByLabelText("Código")).toHaveValue("ING-2024");
  });

  it("shows validation errors for empty required fields", async () => {
    renderWithProviders(<CarreraFormModal {...defaultProps} />);
    const createBtn = screen.getByText("Crear");
    createBtn.click();
    await waitFor(() => {
      expect(screen.getByText("El código es requerido")).toBeInTheDocument();
      expect(screen.getByText("El nombre es requerido")).toBeInTheDocument();
    });
  });

  it("does not render when closed", () => {
    renderWithProviders(<CarreraFormModal {...defaultProps} open={false} />);
    expect(screen.queryByText("Nueva carrera")).not.toBeInTheDocument();
  });
});

describe("AdminCarrerasPage", () => {
  it("renders page header with title", () => {
    renderWithProviders(<AdminCarrerasPage />);
    expect(screen.getByText("Carreras")).toBeInTheDocument();
  });

  it("renders create button", () => {
    renderWithProviders(<AdminCarrerasPage />);
    expect(screen.getByText("Nueva carrera")).toBeInTheDocument();
  });

  it("renders table headers", async () => {
    renderWithProviders(<AdminCarrerasPage />);
    await waitFor(() => {
      expect(screen.getByText("Código")).toBeInTheDocument();
    });
    expect(screen.getByText("Nombre")).toBeInTheDocument();
    expect(screen.getByText("Estado")).toBeInTheDocument();
    expect(screen.getByText("Acciones")).toBeInTheDocument();
  });

  it("opens modal when clicking Nueva carrera", async () => {
    renderWithProviders(<AdminCarrerasPage />);
    screen.getByText("Nueva carrera").click();
    await waitFor(() => {
      expect(screen.getByText("Nueva carrera")).toBeInTheDocument();
    });
  });
});
