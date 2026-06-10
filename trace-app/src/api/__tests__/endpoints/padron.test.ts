import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  padronImportarConfirmar,
  vaciarMateria,
} from "@/api/endpoints/padron";

const BASE = "/api/v1";

describe("padron API", () => {
  beforeEach(() => server.resetHandlers());

  it("padronImportarConfirmar confirms import", async () => {
    server.use(
      http.post(`${BASE}/padron/importar/confirmar`, () =>
        HttpResponse.json({ detail: "Ok", importados: 30 }),
      ),
    );
    const res = await padronImportarConfirmar({ file_token: "pt-1" });
    expect(res.data.importados).toBe(30);
  });

  it("vaciarMateria sends POST with params in URL", async () => {
    server.use(
      http.post(`${BASE}/padron/vaciar/m1/c1`, () =>
        HttpResponse.json({ detail: "Materia vaciada" }),
      ),
    );
    const res = await vaciarMateria("m1", "c1");
    expect(res.data.detail).toBe("Materia vaciada");
  });
});
