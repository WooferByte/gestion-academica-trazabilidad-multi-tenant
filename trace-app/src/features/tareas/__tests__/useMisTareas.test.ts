import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useMisTareas } from "@/features/tareas/hooks/useTareas";

const BASE = "/api/v1";

describe("useMisTareas", () => {
  beforeEach(() => server.resetHandlers());

  it("fetches mis tareas with correct query key", async () => {
    server.use(
      http.get(`${BASE}/tareas/mis-tareas`, () =>
        HttpResponse.json({
          items: [
            {
              id: "t1",
              tenant_id: "t1",
              materia_id: "m1",
              asignado_a: "u1",
              asignado_por: "u2",
              estado: "abierta",
              descripcion: "Corregir TP de Álgebra",
              contexto_id: null,
              comentarios: [],
              created_at: "2026-06-01T00:00:00",
              updated_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    const { result } = renderHook(() => useMisTareas(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].estado).toBe("abierta");
  });

  it("returns empty array when no tareas", async () => {
    server.use(
      http.get(`${BASE}/tareas/mis-tareas`, () =>
        HttpResponse.json({ items: [], total: 0 }),
      ),
    );

    const { result } = renderHook(() => useMisTareas(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(0);
  });
});
