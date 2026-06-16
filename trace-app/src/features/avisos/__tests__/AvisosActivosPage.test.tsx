import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import AvisosActivosPage from "@/features/avisos/pages/AvisosActivosPage";

const BASE = "/api/v1";

describe("AvisosActivosPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders avisos scoped to user", async () => {
    server.use(
      http.get(`${BASE}/avisos`, () =>
        HttpResponse.json({
          items: [
            {
              id: "av1",
              tenant_id: "t1",
              alcance: "Global",
              materia_id: null,
              cohorte_id: null,
              rol_destino: null,
              severidad: "Info",
              titulo: "Aviso Activo",
              cuerpo: "Cuerpo del aviso",
              inicio_vigencia: "2025-01-01T00:00:00",
              fin_vigencia: "2025-12-31T00:00:00",
              orden: 0,
              activo: true,
              requiere_ack: false,
              total_acks: 0,
              user_acked: false,
              created_at: "2025-01-01T00:00:00",
              updated_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    renderWithProviders(<AvisosActivosPage />);

    await waitFor(() => {
      expect(screen.getByText("Aviso Activo")).toBeInTheDocument();
    });
  });

  it("ack button calls confirmarLectura", async () => {
    let ackCalled = false;

    server.use(
      http.get(`${BASE}/avisos`, () =>
        HttpResponse.json({
          items: [
            {
              id: "av1",
              tenant_id: "t1",
              alcance: "Global",
              materia_id: null,
              cohorte_id: null,
              rol_destino: null,
              severidad: "Info",
              titulo: "Aviso con Ack",
              cuerpo: "Cuerpo",
              inicio_vigencia: "2025-01-01T00:00:00",
              fin_vigencia: "2025-12-31T00:00:00",
              orden: 0,
              activo: true,
              requiere_ack: true,
              total_acks: 0,
              user_acked: false,
              created_at: "2025-01-01T00:00:00",
              updated_at: null,
            },
          ],
          total: 1,
        }),
      ),
      http.post(`${BASE}/avisos/av1/ack`, () => {
        ackCalled = true;
        return HttpResponse.json(
          { id: "ack-1", aviso_id: "av1", usuario_id: "u1", confirmado_at: "2025-03-01T12:00:00" },
          { status: 201 },
        );
      }),
    );

    renderWithProviders(<AvisosActivosPage />);

    await waitFor(() => {
      expect(screen.getByText("Aviso con Ack")).toBeInTheDocument();
    });

    const ackButton = screen.getByText("Confirmar lectura");
    fireEvent.click(ackButton);

    await waitFor(() => {
      expect(ackCalled).toBe(true);
    });
  });
});
