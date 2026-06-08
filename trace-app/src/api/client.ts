import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";
import { showToast } from "@/components/ui/Toast";

const TOKEN_PREFIX = "trace_";
const STORAGE_KEYS = {
  ACCESS: `${TOKEN_PREFIX}access_token`,
  REFRESH: `${TOKEN_PREFIX}refresh_token`,
} as const;

function getAccessToken(): string | null {
  return localStorage.getItem(STORAGE_KEYS.ACCESS);
}

function getRefreshToken(): string | null {
  return localStorage.getItem(STORAGE_KEYS.REFRESH);
}

function setTokens(access: string, refresh: string): void {
  localStorage.setItem(STORAGE_KEYS.ACCESS, access);
  localStorage.setItem(STORAGE_KEYS.REFRESH, refresh);
}

function clearTokens(): void {
  localStorage.removeItem(STORAGE_KEYS.ACCESS);
  localStorage.removeItem(STORAGE_KEYS.REFRESH);
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const tenantId = extractTenantFromToken(token);
  if (tenantId && config.headers) {
    config.headers["X-Tenant-ID"] = tenantId;
  }

  return config;
});

function extractTenantFromToken(token: string | null): string | null {
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const decoded = JSON.parse(atob(payload));
    return decoded.tenant_id ?? null;
  } catch {
    return null;
  }
}

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null): void {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (!originalRequest) return Promise.reject(error);

    if (error.response?.status === 403) {
      showToast(
        "No tienes permiso para realizar esta acción",
        "error",
      );
      return Promise.reject(error);
    }

    // No intentar refresh en el endpoint de login
    if (originalRequest.url?.includes("/auth/login")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        window.location.href = "/login?reason=session_expired";
        return Promise.reject(error);
      }

      try {
        const response = await axios.post("/api/v1/auth/refresh", {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        setTokens(access_token, refresh_token);

        processQueue(null, access_token);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        window.location.href = "/login?reason=session_expired";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export { api, setTokens, clearTokens, getAccessToken, STORAGE_KEYS };
export default api;
