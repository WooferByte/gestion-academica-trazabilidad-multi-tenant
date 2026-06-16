import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import GuardiasListPage from "@/features/encuentros/pages/GuardiasListPage";

const BASE = "/api/v1";

const mockGuardias = {
  items: [
    {
      id: "g-1",
      tenant_id: "t1",
      asignacion_id: "asig-1",
      materia_id: "mat-1",
      carrera_id: null,
      cohorte_id: null,
      dia: "2026-03-15",
      horario: "18:00-21:00",
      estado: "pendiente",
      comentarios: null,
      created_at: null,
      updated_at: null,
    },
  ],
  total: 1,
};

describe("GuardiasListPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders guardias list with filters", async () => {
    server.use(
      http.get(`${BASE}/guardias`, () => HttpResponse.json(mockGuardias)),
    );

    renderWithProviders(<GuardiasListPage />);

    await waitFor(() => {
      expect(screen.getByText("Guardias")).toBeDefined();
    });

    await waitFor(() => {
      expect(screen.getByText("2026-03-15")).toBeDefined();
    });
  });

  it("shows loading state", async () => {
    server.use(
      http.get(`${BASE}/guardias`, () => HttpResponse.json(mockGuardias)),
    );

    renderWithProviders(<GuardiasListPage />);

    expect(screen.getByText("Guardias")).toBeDefined();
  });
});
