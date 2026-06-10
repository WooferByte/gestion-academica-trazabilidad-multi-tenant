import { http, HttpResponse } from "msw";

const BASE_URL = "/api/v1";

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
];
