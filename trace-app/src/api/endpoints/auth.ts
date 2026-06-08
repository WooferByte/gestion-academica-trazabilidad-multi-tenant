import api from "@/api/client";
import type {
  LoginRequest,
  LoginResponse,
  Verify2faRequest,
  Verify2faResponse,
  RecoveryRequest,
  RecoveryConfirmRequest,
  ForgotResponse,
  User,
} from "@/api/types";

export function login(data: LoginRequest) {
  return api.post<LoginResponse>("/auth/login", data);
}

export function verify2fa(data: Verify2faRequest) {
  return api.post<Verify2faResponse>("/auth/2fa/verify", data);
}

export function refresh(refreshToken: string) {
  return api.post<{ access_token: string; refresh_token: string; token_type: string }>(
    "/auth/refresh",
    { refresh_token: refreshToken },
  );
}

export function recovery(data: RecoveryRequest) {
  return api.post<ForgotResponse>("/auth/forgot", data);
}

export function recoveryConfirm(data: RecoveryConfirmRequest) {
  return api.post<{ detail: string }>("/auth/reset", data);
}

export function logout() {
  return api.post<{ message: string }>("/auth/logout");
}

export function getMe() {
  return api.get<User>("/auth/me");
}
