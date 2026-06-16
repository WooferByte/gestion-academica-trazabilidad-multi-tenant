import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { createWrapper } from "@/test/test-utils";
import { renderHook, waitFor } from "@testing-library/react";
import { useAgregarComentario } from "@/features/tareas/hooks/useTareaComentarios";

const BASE = "/api/v1";

describe("Agregar comentario a tarea", () => {
  beforeEach(() => server.resetHandlers());

  it("adds comment to tarea successfully", async () => {
    server.use(
      http.post(`${BASE}/tareas/t1/comentarios`, () =>
        HttpResponse.json({
          id: "c1",
          tarea_id: "t1",
          autor_id: "u1",
          texto: "Nuevo comentario de prueba",
          creado_at: "2026-06-02T00:00:00",
        }),
      ),
    );

    const { result } = renderHook(() => useAgregarComentario("t1"), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ texto: "Nuevo comentario de prueba" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.texto).toBe("Nuevo comentario de prueba");
    expect(result.current.data?.tarea_id).toBe("t1");
  });
});
