export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  roles: string[];
  permisos: string[];
  tenant_id: string;
}

export interface Session {
  user: User;
  permissions: string[];
  impersonating: boolean;
  original_user?: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface Verify2faData {
  code: string;
  temp_token: string;
}

export interface RecoveryRequestData {
  email: string;
}

export interface RecoveryConfirmData {
  email: string;
  code: string;
  new_password: string;
}

export type LoginStep = "credentials" | "2fa" | "complete";

export interface AuthState {
  user: User | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  impersonating: boolean;
  loginStep: LoginStep;
  tempToken: string | null;
}
