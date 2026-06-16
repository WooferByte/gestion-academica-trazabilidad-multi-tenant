import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders, createWrapper } from "@/test/test-utils";
import { renderHook, waitFor } from "@testing-library/react";
import { useCambiarEstado } from "@/features/tareas/hooks/useTareas";

const BASE = "/api/v1";

describe("Cambiar estado de tarea", () => {
  beforeEach(() => server.resetHandlers());

  it("changes estado from abierta to en_progreso", async () => {
    server.use(
      http.patch(`${BASE}/tareas/:id/estado`, ({ params }) =>
        HttpResponse.json({
          id: params.id,
          tenant_id: "t1",
          materia_id: "m1",
          asignado_a: "u1",
          asignado_por: "u2",
          estado: "en_progreso",
          descripcion: "Test tarea",
          contexto_id: null,
          comentarios: [],
          created_at: "2026-06-01T00:00:00",
          updated_at: "2026-06-02T00:00:00",
        }),
      ),
    );

    const { result } = renderHook(() => useCambiarEstado(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ id: "t1", data: { estado: "en_progreso" } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.estado).toBe("en_progreso");
  });
});
