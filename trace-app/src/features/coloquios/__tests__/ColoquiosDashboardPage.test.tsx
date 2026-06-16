import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import ColoquiosDashboardPage from "@/features/coloquios/pages/ColoquiosDashboardPage";

const BASE = "/api/v1";

const mockMetricas = {
  total_convocatorias_activas: 5,
  total_alumnos_convocados: 120,
  total_reservas_activas: 45,
  total_resultados_registrados: 30,
};

const mockConvocatorias = {
  items: [],
  total: 0,
};

describe("ColoquiosDashboardPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders metricas cards", async () => {
    server.use(
      http.get(`${BASE}/coloquios/metricas`, () => HttpResponse.json(mockMetricas)),
      http.get(`${BASE}/coloquios/`, () => HttpResponse.json(mockConvocatorias)),
    );

    renderWithProviders(<ColoquiosDashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Coloquios")).toBeDefined();
    });

    await waitFor(() => {
      expect(screen.getByText("5")).toBeDefined();
      expect(screen.getByText("120")).toBeDefined();
    });
  });
});
