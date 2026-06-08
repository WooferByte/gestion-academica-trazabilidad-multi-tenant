export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  requires_2fa: boolean;
}

export interface Verify2faRequest {
  code: string;
  temp_token: string;
}

export interface Verify2faResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RecoveryRequest {
  email: string;
}

export interface RecoveryConfirmRequest {
  token: string;
  new_password: string;
}

export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  roles: string[];
  permisos: string[];
  tenant_id: string;
}

export interface ForgotResponse {
  detail: string;
  token?: string;
  expires_in?: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}
