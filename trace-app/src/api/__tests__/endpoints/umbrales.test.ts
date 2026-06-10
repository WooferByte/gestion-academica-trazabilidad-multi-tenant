import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { getUmbral, updateUmbral } from "@/api/endpoints/umbrales";

const BASE = "/api/v1";

describe("umbrales API", () => {
  beforeEach(() => server.resetHandlers());

  it("getUmbral returns current value", async () => {
    server.use(
      http.get(`${BASE}/umbrales/m1/c1`, () =>
        HttpResponse.json({ materia_id: "m1", cohorte_id: "c1", umbral: 70 }),
      ),
    );
    const res = await getUmbral("m1", "c1");
    expect(res.data.umbral).toBe(70);
  });

  it("updateUmbral sends PUT with new value", async () => {
    server.use(
      http.put(`${BASE}/umbrales/m1/c1`, () =>
        HttpResponse.json({ materia_id: "m1", cohorte_id: "c1", umbral: 80 }),
      ),
    );
    const res = await updateUmbral("m1", "c1", { umbral: 80 });
    expect(res.data.umbral).toBe(80);
  });
});
