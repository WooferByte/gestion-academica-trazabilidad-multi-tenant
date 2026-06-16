import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useConfirmarLectura } from "@/features/avisos/hooks/useConfirmarLectura";

const BASE = "/api/v1";

describe("useConfirmarLectura", () => {
  beforeEach(() => server.resetHandlers());

  it("sends POST to /avisos/{id}/ack", async () => {
    let capturedPath = "";

    server.use(
      http.post(`${BASE}/avisos/:id/ack`, async ({ params }) => {
        capturedPath = `/avisos/${params.id}/ack`;
        return HttpResponse.json(
          {
            id: "ack-1",
            aviso_id: params.id as string,
            usuario_id: "u1",
            confirmado_at: "2025-03-01T12:00:00",
          },
          { status: 201 },
        );
      }),
    );

    const { result } = renderHook(() => useConfirmarLectura(), {
      wrapper: createWrapper(),
    });

    result.current.mutate("av1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(capturedPath).toBe("/avisos/av1/ack");
    expect(result.current.data?.aviso_id).toBe("av1");
  });
});
