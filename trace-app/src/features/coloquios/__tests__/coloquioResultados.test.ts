import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useResultadosList, useRegistrarResultado } from "@/features/coloquios/hooks/useColoquioResultados";

const BASE = "/api/v1";

const mockResultados = {
  items: [
    {
      id: "res-1",
      evaluacion_id: "ev-1",
      alumno_id: "al-1",
      nota_final: "8",
      created_at: "2026-06-01T00:00:00",
      updated_at: null,
    },
  ],
  total: 1,
};

describe("useColoquioResultados", () => {
  beforeEach(() => server.resetHandlers());

  it("returns resultados list", async () => {
    server.use(
      http.get(`${BASE}/coloquios/ev-1/resultados`, () => HttpResponse.json(mockResultados)),
    );

    const { result } = renderHook(() => useResultadosList("ev-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].nota_final).toBe("8");
  });

  it("registers a resultado", async () => {
    server.use(
      http.put(`${BASE}/coloquios/ev-1/resultados/al-1`, () =>
        HttpResponse.json(mockResultados.items[0], { status: 200 }),
      ),
    );

    const { result } = renderHook(() => useRegistrarResultado(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      evaluacionId: "ev-1",
      alumnoId: "al-1",
      data: { nota_final: "8" },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.nota_final).toBe("8");
  });
});
