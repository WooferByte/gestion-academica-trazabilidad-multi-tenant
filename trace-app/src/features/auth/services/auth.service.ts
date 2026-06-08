import type {
  LoginRequest,
  Verify2faRequest,
  RecoveryRequest,
  RecoveryConfirmRequest,
} from "@/api/types";
import * as authApi from "@/api/endpoints/auth";
import { setTokens, clearTokens } from "@/api/client";

export async function loginService(data: LoginRequest) {
  const response = await authApi.login(data);
  const result = response.data;

  if (result.requires_2fa) {
    return {
      requires_2fa: true,
      temp_token: result.access_token,
      access_token: null,
      refresh_token: null,
    };
  }

  setTokens(result.access_token, result.refresh_token);
  return {
    requires_2fa: false,
    temp_token: null,
    access_token: result.access_token,
    refresh_token: result.refresh_token,
  };
}

export async function verify2faService(data: Verify2faRequest) {
  const response = await authApi.verify2fa(data);
  const result = response.data;
  setTokens(result.access_token, result.refresh_token);
  return result;
}

export async function logoutService() {
  try {
    await authApi.logout();
  } finally {
    clearTokens();
  }
}

export async function getMeService() {
  const response = await authApi.getMe();
  return response.data;
}

export async function requestRecoveryService(data: RecoveryRequest) {
  const response = await authApi.recovery(data);
  return response.data;
}

export async function confirmRecoveryService(data: RecoveryConfirmRequest) {
  const response = await authApi.recoveryConfirm(data);
  return response.data;
}

export function hasPermission(
  userPermissions: string[],
  required: string | string[],
): boolean {
  const requiredPerms = Array.isArray(required) ? required : [required];
  return requiredPerms.every((p) => userPermissions.includes(p));
}
