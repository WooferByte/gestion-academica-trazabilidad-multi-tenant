import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { createWrapper } from "@/test/test-utils";
import { renderHook, waitFor } from "@testing-library/react";
import { useActualizarTarea } from "@/features/tareas/hooks/useTareas";

const BASE = "/api/v1";

describe("Delegar tarea a otro docente", () => {
  beforeEach(() => server.resetHandlers());

  it("delegates task by changing asignado_a", async () => {
    const nuevoAsignado = "u3";

    server.use(
      http.patch(`${BASE}/tareas/:id`, ({ params }) =>
        HttpResponse.json({
          id: params.id,
          tenant_id: "t1",
          materia_id: "m1",
          asignado_a: nuevoAsignado,
          asignado_por: "u1",
          estado: "abierta",
          descripcion: "Test tarea delegada",
          contexto_id: null,
          comentarios: [],
          created_at: "2026-06-01T00:00:00",
          updated_at: "2026-06-02T00:00:00",
        }),
      ),
    );

    const { result } = renderHook(() => useActualizarTarea(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ id: "t1", data: { asignado_a: nuevoAsignado } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.asignado_a).toBe(nuevoAsignado);
  });
});
