import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  getAtrasados,
  getRanking,
  getNotasFinales,
  getTpsSinCorregir,
  getReportesRapidos,
  getMonitorSeguimiento,
  getMonitorGeneral,
} from "@/api/endpoints/analisis";

const BASE = "/api/v1";

describe("analisis API", () => {
  beforeEach(() => server.resetHandlers());

  it("getAtrasados returns students", async () => {
    server.use(
      http.get(`${BASE}/analisis/atrasados`, () =>
        HttpResponse.json({ alumnos: [{ id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", actividades_totales: 5, actividades_aprobadas: 2, estado: "faltantes" }] }),
      ),
    );
    const res = await getAtrasados({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.alumnos).toHaveLength(1);
  });

  it("getRanking returns sorted list", async () => {
    server.use(
      http.get(`${BASE}/analisis/ranking`, () =>
        HttpResponse.json({ alumnos: [{ id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", actividades_aprobadas: 8, actividades_totales: 10, porcentaje: 80 }] }),
      ),
    );
    const res = await getRanking({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.alumnos?.[0]?.porcentaje).toBe(80);
  });

  it("getNotasFinales returns grade matrix", async () => {
    server.use(
      http.get(`${BASE}/analisis/notas-finales`, () =>
        HttpResponse.json({ actividades: [{ id: "act1", nombre: "TP1", tipo: "tp", fecha: "" }], alumnos: [{ alumno_id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", notas: { act1: 8 } }] }),
      ),
    );
    const res = await getNotasFinales({ materia_id: "m1", cohorte_id: "c1", actividades: "act1" });
    expect(res.data.actividades).toHaveLength(1);
  });

  it("getTpsSinCorregir returns pending TPs", async () => {
    server.use(
      http.get(`${BASE}/analisis/tps-sin-corregir`, () =>
        HttpResponse.json({ tps: [{ id: "tp1", alumno_id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", actividad_nombre: "TP1", actividad_tipo: "tp", fecha_entrega: "2024-01-01" }] }),
      ),
    );
    const res = await getTpsSinCorregir({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.tps).toHaveLength(1);
  });

  it("getReportesRapidos returns KPIs", async () => {
    server.use(
      http.get(`${BASE}/analisis/reportes-rapidos`, () =>
        HttpResponse.json({ materia_id: "m1", cohorte_id: "c1", kpis: { total_alumnos: 30, total_actividades: 5, aprobados: 20, atrasados: 10, promedio_general: 65 } }),
      ),
    );
    const res = await getReportesRapidos({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.kpis.total_alumnos).toBe(30);
  });

  it("getMonitorSeguimiento returns items", async () => {
    server.use(
      http.get(`${BASE}/analisis/monitor-seguimiento`, () =>
        HttpResponse.json({ items: [{ alumno_id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", materia: "Matemática", comision: "A", actividades_aprobadas: 5, actividades_totales: 10, porcentaje: 50, ultima_actividad: "" }] }),
      ),
    );
    const res = await getMonitorSeguimiento();
    expect(res.data.items).toHaveLength(1);
  });

  it("getMonitorGeneral returns aggregated data", async () => {
    server.use(
      http.get(`${BASE}/analisis/monitor-general`, () =>
        HttpResponse.json({ items: [{ alumno_id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", materia: "Matemática", comision: "A", actividades_aprobadas: 5, actividades_totales: 10, porcentaje: 50, ultima_actividad: "" }] }),
      ),
    );
    const res = await getMonitorGeneral();
    expect(res.data.items).toHaveLength(1);
  });
});
