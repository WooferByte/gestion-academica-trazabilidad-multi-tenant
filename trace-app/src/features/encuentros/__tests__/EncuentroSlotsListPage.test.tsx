import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import EncuentroSlotsListPage from "@/features/encuentros/pages/EncuentroSlotsListPage";

const BASE = "/api/v1";

const mockSlots = {
  items: [
    {
      id: "slot-1",
      tenant_id: "t1",
      asignacion_id: "asig-1",
      materia_id: "mat-1",
      titulo: "Clase 1",
      hora: "18:00",
      dia_semana: "LUNES",
      fecha_inicio: "2026-03-01",
      cant_semanas: 8,
      fecha_unica: null,
      meet_url: null,
      vig_desde: null,
      vig_hasta: null,
      created_at: null,
      updated_at: null,
    },
  ],
  total: 1,
};

describe("EncuentroSlotsListPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders slots list", async () => {
    server.use(
      http.get(`${BASE}/encuentros/slots`, () => HttpResponse.json(mockSlots)),
    );

    renderWithProviders(<EncuentroSlotsListPage />);

    await waitFor(() => {
      expect(screen.getByText("Encuentros")).toBeDefined();
    });

    await waitFor(() => {
      expect(screen.getByText("Clase 1")).toBeDefined();
    });
  });
});
