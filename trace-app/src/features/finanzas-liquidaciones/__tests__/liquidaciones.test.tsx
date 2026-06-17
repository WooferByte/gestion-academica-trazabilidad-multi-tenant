import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import {
  getLiquidaciones,
  calcularLiquidacion,
  cerrarLiquidacion,
  getHistorial,
  exportarLiquidaciones,
} from "../services/liquidaciones.service";
import FinanzasLiquidacionesPage from "../pages/FinanzasLiquidacionesPage";
import FinanzasLiquidacionesHistorialPage from "../pages/FinanzasLiquidacionesHistorialPage";
import { CalcularLiquidacionDialog } from "../components/CalcularLiquidacionDialog";
import { CerrarLiquidacionDialog } from "../components/CerrarLiquidacionDialog";

describe("Liquidaciones Service", () => {
  it("getLiquidaciones returns bare array", async () => {
    const res = await getLiquidaciones();
    expect(res.status).toBe(200);
    expect(Array.isArray(res.data)).toBe(true);
    if (res.data.length > 0) {
      expect(res.data[0]).toHaveProperty("id");
      expect(res.data[0]).toHaveProperty("usuario_id");
      expect(res.data[0]).toHaveProperty("cohorte_id");
      expect(res.data[0]).toHaveProperty("periodo");
      expect(res.data[0]).toHaveProperty("rol");
      expect(res.data[0]).toHaveProperty("monto_base");
      expect(res.data[0]).toHaveProperty("monto_plus");
      expect(res.data[0]).toHaveProperty("total");
      expect(res.data[0]).toHaveProperty("es_nexo");
      expect(res.data[0]).toHaveProperty("excluido_por_factura");
      expect(res.data[0]).toHaveProperty("estado");
    }
  });

  it("getLiquidaciones filters by cohorte_id", async () => {
    const res = await getLiquidaciones({ cohorte_id: "coh-1" });
    expect(res.data.every((l) => l.cohorte_id === "coh-1")).toBe(true);
  });

  it("getLiquidaciones filters by periodo", async () => {
    const res = await getLiquidaciones({ periodo: "2025-01" });
    expect(res.data.every((l) => l.periodo === "2025-01")).toBe(true);
  });

  it("calcularLiquidacion sends POST and returns array", async () => {
    const res = await calcularLiquidacion({ cohorte_id: "coh-1", periodo: "2025-03" });
    expect(res.status).toBe(201);
    expect(Array.isArray(res.data)).toBe(true);
    if (res.data.length > 0 && res.data[0]) {
      expect(res.data[0].estado).toBe("calculada");
    }
  });

  it("cerrarLiquidacion sends POST and returns CerrarResponse", async () => {
    const res = await cerrarLiquidacion("coh-1", "2025-01");
    expect(res.status).toBe(200);
    expect(res.data).toHaveProperty("cerradas");
    expect(res.data).toHaveProperty("periodo");
    expect(typeof res.data.cerradas).toBe("number");
    expect(res.data.periodo).toBe("2025-01");
  });

  it("getHistorial returns only cerradas", async () => {
    const res = await getHistorial();
    expect(Array.isArray(res.data)).toBe(true);
    expect(res.data.every((l) => l.estado === "cerrada")).toBe(true);
  });

  it("exportarLiquidaciones returns blob", async () => {
    const res = await exportarLiquidaciones("coh-1", "2025-01");
    expect(res.data instanceof Blob).toBe(true);
  });

  it("getLiquidaciones returns bare array (not {items, total})", async () => {
    const res = await getLiquidaciones();
    expect(res.data).not.toHaveProperty("items");
    expect(res.data).not.toHaveProperty("total");
  });
});

describe("CalcularLiquidacionDialog", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
  };

  it("renders with title and form fields", () => {
    renderWithProviders(<CalcularLiquidacionDialog {...defaultProps} />);
    expect(screen.getByText("Calcular Liquidaciones")).toBeInTheDocument();
    expect(screen.getByLabelText("Cohorte ID")).toBeInTheDocument();
    expect(screen.getByLabelText("Período")).toBeInTheDocument();
  });

  it("disables submit when fields are empty", () => {
    renderWithProviders(<CalcularLiquidacionDialog {...defaultProps} />);
    const submitBtn = screen.getByText("Calcular").closest("button");
    expect(submitBtn).toBeDisabled();
  });

  it("shows cancel button", () => {
    renderWithProviders(<CalcularLiquidacionDialog {...defaultProps} />);
    expect(screen.getByText("Cancelar")).toBeInTheDocument();
  });
});

describe("CerrarLiquidacionDialog", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
  };

  it("renders with warning message", () => {
    renderWithProviders(<CerrarLiquidacionDialog {...defaultProps} />);
    expect(screen.getByText("Cerrar Liquidaciones")).toBeInTheDocument();
    expect(screen.getByText(/no se puede deshacer/i)).toBeInTheDocument();
  });

  it("disables confirm when fields are empty", () => {
    renderWithProviders(<CerrarLiquidacionDialog {...defaultProps} />);
    const confirmBtn = screen.getByText("Cerrar").closest("button");
    expect(confirmBtn).toBeDisabled();
  });
});

describe("FinanzasLiquidacionesPage", () => {
  it("renders page header", () => {
    renderWithProviders(<FinanzasLiquidacionesPage />);
    expect(screen.getByText("Liquidaciones")).toBeInTheDocument();
    expect(screen.getByText("Historial")).toBeInTheDocument();
  });

  it("renders action buttons", () => {
    renderWithProviders(<FinanzasLiquidacionesPage />);
    expect(screen.getByText("Calcular")).toBeInTheDocument();
    expect(screen.getByText("Cerrar")).toBeInTheDocument();
  });

  it("renders filter inputs", () => {
    renderWithProviders(<FinanzasLiquidacionesPage />);
    expect(screen.getByText("Cohorte")).toBeInTheDocument();
    expect(screen.getByText("Período")).toBeInTheDocument();
    expect(screen.getByText("Usuario")).toBeInTheDocument();
  });

  it("renders table headers", async () => {
    renderWithProviders(<FinanzasLiquidacionesPage />);
    expect(await screen.findByText("Rol")).toBeInTheDocument();
    expect(screen.getByText("Monto Base")).toBeInTheDocument();
    expect(screen.getByText("Total")).toBeInTheDocument();
  });
});

describe("FinanzasLiquidacionesHistorialPage", () => {
  it("renders historial header", () => {
    renderWithProviders(<FinanzasLiquidacionesHistorialPage />);
    expect(screen.getByText("Historial de Liquidaciones")).toBeInTheDocument();
  });

  it("renders filters", () => {
    renderWithProviders(<FinanzasLiquidacionesHistorialPage />);
    expect(screen.getByText("Cohorte")).toBeInTheDocument();
    expect(screen.getByText("Período")).toBeInTheDocument();
  });
});
