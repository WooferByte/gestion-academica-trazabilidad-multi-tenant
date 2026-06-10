import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import api from "@/api/client";

const BASE_URL = "/api/v1";

describe("Axios interceptor", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("injects Bearer token", async () => {
    localStorage.setItem("trace_access_token", "test-token");

    const requestInterceptor = api.interceptors.request as unknown as {
      handlers: Array<{
        fulfilled: (config: Record<string, unknown>) => Record<string, unknown>;
      }>;
    };

    const handler = requestInterceptor.handlers[0];
    if (handler) {
      const config = handler.fulfilled({
        headers: {},
        url: "/test",
      });

      expect((config.headers as Record<string, string>).Authorization).toBe(
        "Bearer test-token",
      );
    }
  });

  it("extracts tenant_id from token and sets X-Tenant-ID header", () => {
    // Create a token with tenant_id in payload
    const payload = btoa(JSON.stringify({ tenant_id: "tenant-1" }));
    const token = `header.${payload}.signature`;
    localStorage.setItem("trace_access_token", token);

    const requestInterceptor = api.interceptors.request as unknown as {
      handlers: Array<{
        fulfilled: (config: Record<string, unknown>) => Record<string, unknown>;
      }>;
    };

    const handler = requestInterceptor.handlers[0];
    if (handler) {
      const config = handler.fulfilled({
        headers: {},
        url: "/test",
      });

      expect((config.headers as Record<string, string>)["X-Tenant-ID"]).toBe(
        "tenant-1",
      );
    }
  });

  it("refreshes token on 401 and replays the original request", async () => {
    localStorage.setItem("trace_access_token", "expired-token");
    localStorage.setItem("trace_refresh_token", "valid-refresh-token");

    const testPath = `${BASE_URL}/test-refresh-replay`;

    // First call returns 401, retry succeeds
    server.use(
      http.get(
        testPath,
        () =>
          HttpResponse.json({ error: "Unauthorized" }, { status: 401 }),
        { once: true },
      ),
      http.get(testPath, () =>
        HttpResponse.json({ data: "retried successfully" }),
      ),
    );

    const response = await api.get("/test-refresh-replay");
    expect(response.status).toBe(200);
    expect(response.data).toEqual({ data: "retried successfully" });
    // Token should have been refreshed via the default MSW handler
    expect(localStorage.getItem("trace_access_token")).toBe(
      "new-access-token",
    );
    expect(localStorage.getItem("trace_refresh_token")).toBe(
      "new-refresh-token",
    );
  });

  it("clears tokens on failed refresh after 401", async () => {
    localStorage.setItem("trace_access_token", "expired-token");
    localStorage.setItem("trace_refresh_token", "valid-refresh-token");

    const testPath = `${BASE_URL}/test-refresh-fail`;
    server.use(
      http.get(testPath, () =>
        HttpResponse.json({ error: "Unauthorized" }, { status: 401 }),
      ),
      http.post(`${BASE_URL}/auth/refresh`, () =>
        HttpResponse.json(
          { detail: "Invalid refresh token" },
          { status: 401 },
        ),
      ),
    );

    let caughtStatus: number | undefined;
    try {
      await api.get("/test-refresh-fail");
    } catch (err: unknown) {
      caughtStatus = (err as { response?: { status?: number } })?.response?.status;
    }

    expect(caughtStatus).toBe(401);
    // clearTokens() was called - tokens are gone
    expect(localStorage.getItem("trace_access_token")).toBeNull();
    expect(localStorage.getItem("trace_refresh_token")).toBeNull();
  });
});
