import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  previewComunicacion,
  enviarComunicacion,
  enviarLote,
  aprobarLote,
  cancelarComunicacion,
  getComunicacionesTracking,
} from "@/api/endpoints/comunicaciones";

const BASE = "/api/v1";

describe("comunicaciones API", () => {
  beforeEach(() => server.resetHandlers());

  it("previewComunicacion returns HTML preview", async () => {
    server.use(
      http.post(`${BASE}/comunicaciones/preview`, () =>
        HttpResponse.json({ html: "<p>Hola</p>", destinatarios_count: 5, preview_destinatarios: ["Juan"] }),
      ),
    );
    const res = await previewComunicacion({ destinatarios: ["a1"], mensaje: "Hola" });
    expect(res.data.html).toBe("<p>Hola</p>");
  });

  it("enviarComunicacion sends individual", async () => {
    server.use(
      http.post(`${BASE}/comunicaciones`, () =>
        HttpResponse.json({ id: "comm-1", detail: "Enviado" }),
      ),
    );
    const res = await enviarComunicacion({ destinatarios: ["a1"], mensaje: "Hola" });
    expect(res.data.id).toBe("comm-1");
  });

  it("enviarLote sends batch", async () => {
    server.use(
      http.post(`${BASE}/comunicaciones/lote`, () =>
        HttpResponse.json({ id: "lote-1", lote_id: "lote-1", detail: "Lote creado" }),
      ),
    );
    const res = await enviarLote({ destinatarios: ["a1"], mensaje: "Hola" });
    expect(res.data.lote_id).toBe("lote-1");
  });

  it("aprobarLote approves pending lote", async () => {
    server.use(
      http.post(`${BASE}/comunicaciones/aprobar-lote`, () =>
        HttpResponse.json({ detail: "Lote aprobado" }),
      ),
    );
    const res = await aprobarLote({ lote_id: "lote-1" });
    expect(res.data.detail).toBe("Lote aprobado");
  });

  it("cancelarComunicacion cancels pending", async () => {
    server.use(
      http.post(`${BASE}/comunicaciones/comm-1/cancelar`, () =>
        HttpResponse.json({ detail: "Cancelado" }),
      ),
    );
    const res = await cancelarComunicacion("comm-1");
    expect(res.data.detail).toBe("Cancelado");
  });

  it("getComunicacionesTracking returns tracking", async () => {
    server.use(
      http.get(`${BASE}/comunicaciones`, () =>
        HttpResponse.json({ items: [{ id: "c1", alumno_id: "a1", nombre: "Juan", apellido: "Pérez", estado: "enviado", timestamp: "2024-01-01" }], lote_id: "lote-1", lote_estado: "enviado" }),
      ),
    );
    const res = await getComunicacionesTracking({ lote_id: "lote-1" });
    expect(res.data.items).toHaveLength(1);
  });
});
