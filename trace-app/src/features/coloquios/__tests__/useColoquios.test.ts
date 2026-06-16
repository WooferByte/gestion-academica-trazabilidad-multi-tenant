import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useMetricas, useConvocatoriasList } from "@/features/coloquios/hooks/useColoquios";

const BASE = "/api/v1";

const mockMetricas = {
  total_convocatorias_activas: 5,
  total_alumnos_convocados: 120,
  total_reservas_activas: 45,
  total_resultados_registrados: 30,
};

const mockConvocatorias = {
  items: [
    {
      id: "ev-1",
      tenant_id: "t1",
      materia_id: "mat-1",
      cohorte_id: "coh-1",
      tipo: "final",
      instancia: "1er Final",
      estado: "activa",
      dias_disponibles: 5,
      turnos: [],
      total_convocados: 20,
      reservas_activas: 10,
      cupos_libres: 15,
      created_at: null,
      updated_at: null,
    },
  ],
  total: 1,
};

describe("useColoquios", () => {
  beforeEach(() => server.resetHandlers());

  it("returns metricas", async () => {
    server.use(
      http.get(`${BASE}/coloquios/metricas`, () => HttpResponse.json(mockMetricas)),
    );

    const { result } = renderHook(() => useMetricas(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.total_convocatorias_activas).toBe(5);
    expect(result.current.data?.total_alumnos_convocados).toBe(120);
  });

  it("returns convocatorias list", async () => {
    server.use(
      http.get(`${BASE}/coloquios/`, () => HttpResponse.json(mockConvocatorias)),
    );

    const { result } = renderHook(() => useConvocatoriasList(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].instancia).toBe("1er Final");
  });
});
