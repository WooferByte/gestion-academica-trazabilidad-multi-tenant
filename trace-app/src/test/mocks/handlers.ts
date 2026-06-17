import { http, HttpResponse } from "msw";

const BASE_URL = "/api/v1";

const mockCarreras = [
  { id: "carr-1", codigo: "ING-2024", nombre: "Ingeniería en Sistemas", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "carr-2", codigo: "LIC-2024", nombre: "Licenciatura en Administración", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "carr-3", codigo: "CONT-2024", nombre: "Contador Público", estado: "Inactiva", created_at: "2025-01-01T00:00:00Z" },
];

const mockMaterias = [
  { id: "mat-101", codigo: "MAT-101", nombre: "Matemática I", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "mat-102", codigo: "FIS-101", nombre: "Física I", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "mat-103", codigo: "PROG-101", nombre: "Programación I", estado: "Inactiva", created_at: "2025-01-01T00:00:00Z" },
];

const mockCohortes = [
  { id: "coh-1", nombre: "Cohorte 2024", carrera_id: "carr-1", carrera_nombre: "Ingeniería en Sistemas", anio: 2024, vig_desde: "2024-03-01", vig_hasta: "2025-02-28", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "coh-2", nombre: "Cohorte 2025", carrera_id: "carr-1", carrera_nombre: "Ingeniería en Sistemas", anio: 2025, vig_desde: "2025-03-01", vig_hasta: "2026-02-28", estado: "Activa", created_at: "2025-01-01T00:00:00Z" },
  { id: "coh-3", nombre: "Cohorte 2024 ADM", carrera_id: "carr-2", carrera_nombre: "Licenciatura en Administración", anio: 2024, vig_desde: "2024-03-01", vig_hasta: "2025-02-28", estado: "Inactiva", created_at: "2025-01-01T00:00:00Z" },
];

const mockDocentes = [
  { id: "doc-1", nombre: "Ana", apellido: "Profesor", email: "ana@test.com", rol: "PROFESOR" },
  { id: "doc-2", nombre: "Carlos", apellido: "Tutor", email: "carlos@test.com", rol: "TUTOR" },
  { id: "doc-3", nombre: "Lucía", apellido: "Nexo", email: "lucia@test.com", rol: "NEXO" },
];

const mockLiquidaciones = [
  { id: "liq-1", usuario_id: "doc-1", cohorte_id: "coh-1", periodo: "2025-01", rol: "PROFESOR", monto_base: 150000, monto_plus: 5000, total: 155000, es_nexo: false, excluido_por_factura: false, estado: "calculada" },
  { id: "liq-2", usuario_id: "doc-2", cohorte_id: "coh-1", periodo: "2025-01", rol: "TUTOR", monto_base: 80000, monto_plus: 2000, total: 82000, es_nexo: false, excluido_por_factura: false, estado: "calculada" },
  { id: "liq-3", usuario_id: "doc-3", cohorte_id: "coh-1", periodo: "2025-01", rol: "NEXO", monto_base: 120000, monto_plus: 0, total: 120000, es_nexo: true, excluido_por_factura: false, estado: "calculada" },
  { id: "liq-4", usuario_id: "doc-1", cohorte_id: "coh-2", periodo: "2025-02", rol: "PROFESOR", monto_base: 150000, monto_plus: 10000, total: 160000, es_nexo: false, excluido_por_factura: false, estado: "cerrada" },
];

const PII_KEYS = ["dni", "cuil", "cbu", "alias_cbu"];

function stripPii<T extends Record<string, unknown>>(obj: T): Omit<T, (typeof PII_KEYS)[number]> {
  const result = { ...obj };
  for (const key of PII_KEYS) {
    delete result[key];
  }
  return result;
}

const mockUsuarios = [
  { id: "user-1", nombre: "Admin", apellido: "Test", email: "admin@test.com", legajo: "LEG-001", banco: "Banco Nación", regional: "Córdoba", facturador: true, roles: ["ADMIN"], estado: "Activo", is_active: true, created_at: "2025-01-01T00:00:00Z" },
  { id: "user-2", nombre: "Juan", apellido: "Pérez", email: "juan@test.com", legajo: "LEG-002", banco: "Banco Córdoba", regional: "Córdoba", facturador: false, roles: ["PROFESOR"], estado: "Activo", is_active: true, created_at: "2025-01-01T00:00:00Z" },
  { id: "user-3", nombre: "María", apellido: "García", email: "maria@test.com", legajo: "LEG-003", banco: "Banco Macro", regional: "Buenos Aires", facturador: true, roles: ["TUTOR"], estado: "Inactivo", is_active: false, created_at: "2025-01-01T00:00:00Z" },
];

export const handlers = [
  // Login success (no 2FA)
  http.post(`${BASE_URL}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;

    if (body.email === "admin@test.com" && body.password === "correct") {
      return HttpResponse.json({
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        token_type: "bearer",
        requires_2fa: false,
      });
    }

    if (body.email === "2fa@test.com" && body.password === "correct") {
      return HttpResponse.json({
        access_token: "temp-2fa-token",
        refresh_token: "mock-refresh-token",
        token_type: "bearer",
        requires_2fa: true,
      });
    }

    return HttpResponse.json(
      { detail: "Credenciales inválidas" },
      { status: 401 },
    );
  }),

  // 2FA verify
  http.post(`${BASE_URL}/auth/2fa/verify`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;

    if (body.code === "123456") {
      return HttpResponse.json({
        access_token: "mock-access-token-after-2fa",
        refresh_token: "mock-refresh-token",
        token_type: "bearer",
      });
    }

    return HttpResponse.json(
      { detail: "Código inválido" },
      { status: 401 },
    );
  }),

  // Get current user
  http.get(`${BASE_URL}/auth/me`, () => {
    return HttpResponse.json({
      id: "user-1",
      email: "admin@test.com",
      nombre: "Admin",
      apellido: "Test",
      roles: ["ADMIN"],
      permisos: [
        "dashboard:ver",
        "academico:ver",
        "analisis:ver",
        "comunicacion:ver",
        "equipos:ver",
        "encuentros:ver",
        "coloquios:ver",
        "liquidaciones:ver",
      ],
      tenant_id: "tenant-1",
    });
  }),

  // Logout
  http.post(`${BASE_URL}/auth/logout`, () => {
    return HttpResponse.json({ message: "Sesión cerrada" });
  }),

  // Recovery
  http.post(`${BASE_URL}/auth/recovery`, () => {
    return HttpResponse.json({ message: "Si el email existe, recibirás instrucciones" });
  }),

  // Recovery confirm
  http.post(`${BASE_URL}/auth/recovery/confirm`, () => {
    return HttpResponse.json({ message: "Contraseña actualizada" });
  }),

  // Token refresh
  http.post(`${BASE_URL}/auth/refresh`, () => {
    return HttpResponse.json({
      access_token: "new-access-token",
      refresh_token: "new-refresh-token",
      token_type: "bearer",
    });
  }),

  // Admin - Carreras
  http.get(`${BASE_URL}/admin/carreras`, ({ request }) => {
    const url = new URL(request.url);
    const activo = url.searchParams.get("activo");
    let result = mockCarreras;
    if (activo === "true") result = mockCarreras.filter((c) => c.estado === "Activa");
    if (activo === "false") result = mockCarreras.filter((c) => c.estado !== "Activa");
    return HttpResponse.json({ items: result, total: result.length });
  }),
  http.get(`${BASE_URL}/admin/carreras/:id`, ({ params }) => {
    const carrera = mockCarreras.find((c) => c.id === params.id);
    if (!carrera) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    return HttpResponse.json(carrera);
  }),
  http.post(`${BASE_URL}/admin/carreras`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const newCarrera = { id: `carr-${Date.now()}`, ...body, estado: "Activa", created_at: new Date().toISOString() };
    mockCarreras.push(newCarrera as typeof mockCarreras[0]);
    return HttpResponse.json(newCarrera, { status: 201 });
  }),
  http.put(`${BASE_URL}/admin/carreras/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const index = mockCarreras.findIndex((c) => c.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockCarreras[index] = { ...mockCarreras[index], ...body } as typeof mockCarreras[0];
    return HttpResponse.json(mockCarreras[index]);
  }),
  http.delete(`${BASE_URL}/admin/carreras/:id`, ({ params }) => {
    const index = mockCarreras.findIndex((c) => c.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockCarreras.splice(index, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // Admin - Cohortes
  http.get(`${BASE_URL}/admin/cohortes`, ({ request }) => {
    const url = new URL(request.url);
    const carreraId = url.searchParams.get("carrera_id");
    let result = mockCohortes;
    if (carreraId) result = mockCohortes.filter((c) => c.carrera_id === carreraId);
    return HttpResponse.json({ items: result, total: result.length });
  }),
  http.get(`${BASE_URL}/admin/cohortes/:id`, ({ params }) => {
    const cohorte = mockCohortes.find((c) => c.id === params.id);
    if (!cohorte) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    return HttpResponse.json(cohorte);
  }),
  http.post(`${BASE_URL}/admin/cohortes`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const newCohorte = { id: `coh-${Date.now()}`, ...body, estado: "Activa", created_at: new Date().toISOString() };
    mockCohortes.push(newCohorte as typeof mockCohortes[0]);
    return HttpResponse.json(newCohorte, { status: 201 });
  }),
  http.put(`${BASE_URL}/admin/cohortes/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const index = mockCohortes.findIndex((c) => c.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockCohortes[index] = { ...mockCohortes[index], ...body } as typeof mockCohortes[0];
    return HttpResponse.json(mockCohortes[index]);
  }),
  http.delete(`${BASE_URL}/admin/cohortes/:id`, ({ params }) => {
    const index = mockCohortes.findIndex((c) => c.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockCohortes.splice(index, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // Admin - Materias
  http.get(`${BASE_URL}/admin/materias`, ({ request }) => {
    const url = new URL(request.url);
    const activo = url.searchParams.get("activo");
    let result = mockMaterias;
    if (activo === "true") result = mockMaterias.filter((m) => m.estado === "Activa");
    if (activo === "false") result = mockMaterias.filter((m) => m.estado !== "Activa");
    return HttpResponse.json({ items: result, total: result.length });
  }),
  http.get(`${BASE_URL}/admin/materias/:id`, ({ params }) => {
    const materia = mockMaterias.find((m) => m.id === params.id);
    if (!materia) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    return HttpResponse.json(materia);
  }),
  http.post(`${BASE_URL}/admin/materias`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const duplicate = mockMaterias.find((m) => m.codigo === body.codigo);
    if (duplicate) return HttpResponse.json({ detail: "Ya existe una materia con este código" }, { status: 409 });
    const newMateria = { id: `mat-${Date.now()}`, ...body, estado: "Activa", created_at: new Date().toISOString() };
    mockMaterias.push(newMateria as typeof mockMaterias[0]);
    return HttpResponse.json(newMateria, { status: 201 });
  }),
  http.put(`${BASE_URL}/admin/materias/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const index = mockMaterias.findIndex((m) => m.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockMaterias[index] = { ...mockMaterias[index], ...body } as typeof mockMaterias[0];
    return HttpResponse.json(mockMaterias[index]);
  }),
  http.delete(`${BASE_URL}/admin/materias/:id`, ({ params }) => {
    const index = mockMaterias.findIndex((m) => m.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockMaterias.splice(index, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // Admin - Usuarios (PII NEVER exposed in any response)
  http.get(`${BASE_URL}/admin/usuarios`, ({ request }) => {
    const url = new URL(request.url);
    const activo = url.searchParams.get("activo");
    let result = mockUsuarios.map((u) => stripPii(u));
    if (activo === "true") result = result.filter((u) => u.estado === "Activa");
    if (activo === "false") result = result.filter((u) => u.estado !== "Activa");
    return HttpResponse.json({ items: result, total: result.length });
  }),
  http.get(`${BASE_URL}/admin/usuarios/:id`, ({ params }) => {
    const usuario = mockUsuarios.find((u) => u.id === params.id);
    if (!usuario) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    return HttpResponse.json(stripPii(usuario));
  }),
  http.post(`${BASE_URL}/admin/usuarios`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const newUsuario = { id: `user-${Date.now()}`, ...body, estado: "Activa", roles: ["PROFESOR"], created_at: new Date().toISOString() } as Record<string, unknown>;
    mockUsuarios.push(newUsuario as typeof mockUsuarios[0]);
    return HttpResponse.json(stripPii(newUsuario), { status: 201 });
  }),
  http.put(`${BASE_URL}/admin/usuarios/:id`, async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const index = mockUsuarios.findIndex((u) => u.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockUsuarios[index] = { ...mockUsuarios[index], ...body } as typeof mockUsuarios[0];
    return HttpResponse.json(stripPii(mockUsuarios[index]));
  }),
  http.delete(`${BASE_URL}/admin/usuarios/:id`, ({ params }) => {
    const index = mockUsuarios.findIndex((u) => u.id === params.id);
    if (index === -1) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    mockUsuarios.splice(index, 1);
    return HttpResponse.json(null, { status: 204 });
  }),

  // Auditoria Panel - ActionsPerDay
  http.get(`${BASE_URL}/auditoria/acciones-por-dia`, () => {
    return HttpResponse.json([
      { fecha: "2025-06-01", accion: "login", total: 45 },
      { fecha: "2025-06-02", accion: "login", total: 52 },
      { fecha: "2025-06-03", accion: "login", total: 38 },
      { fecha: "2025-06-04", accion: "login", total: 61 },
      { fecha: "2025-06-05", accion: "login", total: 47 },
    ]);
  }),

  // Auditoria Panel - CommsStatus
  http.get(`${BASE_URL}/auditoria/comunicaciones-por-docente`, () => {
    return HttpResponse.json([
      {
        usuario_id: "user-1",
        docente_email: "ana.profesor@test.com",
        pendientes: 12,
        enviadas: 45,
        fallidas: 2,
      },
      {
        usuario_id: "user-2",
        docente_email: "carlos.profesor@test.com",
        pendientes: 8,
        enviadas: 32,
        fallidas: 0,
      },
    ]);
  }),

  // Auditoria Panel - Interactions
  http.get(`${BASE_URL}/auditoria/interacciones-por-docente-materia`, () => {
    return HttpResponse.json([
      { usuario_id: "user-1", materia_id: "mat-101", accion: "consulta", total: 120 },
      { usuario_id: "user-1", materia_id: "mat-101", accion: "update", total: 45 },
      { usuario_id: "user-2", materia_id: "mat-102", accion: "consulta", total: 80 },
    ]);
  }),

  // Auditoria Panel - LastActions (uses /auditoria/log same as audit log)
  http.get(`${BASE_URL}/auditoria/log`, ({ request }) => {
    const url = new URL(request.url);
    const pageSize = parseInt(url.searchParams.get("page_size") ?? "25");

    const items = [
      {
        id: "act-1",
        fecha_hora: "2025-06-05T10:30:00Z",
        actor_id: "user-1",
        materia_id: "mat-1",
        accion: "login",
        filas_afectadas: 1,
        ip: "192.168.1.1",
        user_agent: "Mozilla/5.0",
      },
      {
        id: "act-2",
        fecha_hora: "2025-06-05T09:15:00Z",
        actor_id: "user-2",
        materia_id: "mat-1",
        accion: "update",
        filas_afectadas: 3,
        ip: "192.168.1.2",
        user_agent: "Mozilla/5.0",
      },
      {
        id: "act-3",
        fecha_hora: "2025-06-04T14:00:00Z",
        actor_id: "user-3",
        materia_id: "mat-2",
        accion: "delete",
        filas_afectadas: 5,
        ip: "192.168.1.3",
        user_agent: "PostmanRuntime/7.36.0",
      },
    ];

    return HttpResponse.json(items);
  }),

  // Liquidaciones
  http.get(`${BASE_URL}/liquidaciones`, ({ request }) => {
    const url = new URL(request.url);
    const cohorteId = url.searchParams.get("cohorte_id");
    const periodo = url.searchParams.get("periodo");
    let result = [...mockLiquidaciones];
    if (cohorteId) result = result.filter((l) => l.cohorte_id === cohorteId);
    if (periodo) result = result.filter((l) => l.periodo === periodo);
    return HttpResponse.json(result);
  }),

  http.post(`${BASE_URL}/liquidaciones/calcular`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const newLiquidaciones = mockDocentes.map((d) => ({
      id: `liq-${Date.now()}-${d.id}`,
      usuario_id: d.id,
      cohorte_id: body.cohorte_id,
      periodo: body.periodo,
      rol: d.rol,
      monto_base: 100000,
      monto_plus: 0,
      total: 100000,
      es_nexo: d.rol === "NEXO",
      excluido_por_factura: false,
      estado: "calculada",
    }));
    mockLiquidaciones.push(...newLiquidaciones);
    return HttpResponse.json(newLiquidaciones, { status: 201 });
  }),

  http.post(`${BASE_URL}/liquidaciones/cerrar/:cohorteId/:periodo`, ({ params, request }) => {
    const { cohorteId, periodo } = params;
    const count = mockLiquidaciones.filter(
      (l) => l.cohorte_id === cohorteId && l.periodo === periodo,
    ).length;
    mockLiquidaciones.forEach((l) => {
      if (l.cohorte_id === cohorteId && l.periodo === periodo) {
        l.estado = "cerrada";
      }
    });
    return HttpResponse.json({ cerradas: count, periodo });
  }),

  http.get(`${BASE_URL}/liquidaciones/historial`, () => {
    return HttpResponse.json(mockLiquidaciones.filter((l) => l.estado === "cerrada"));
  }),

  http.get(`${BASE_URL}/liquidaciones/exportar`, () => {
    return HttpResponse.arrayBuffer(new ArrayBuffer(0), {
      headers: { "Content-Type": "text/csv" },
    });
  }),
];
