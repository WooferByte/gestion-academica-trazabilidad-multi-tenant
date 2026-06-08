import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";
import type { User } from "@/features/auth/types/auth.types";
import type {
  LoginRequest,
  Verify2faRequest,
  RecoveryRequest,
  RecoveryConfirmRequest,
} from "@/api/types";
import {
  loginService,
  verify2faService as verify2faSvc,
  getMeService,
  requestRecoveryService,
  confirmRecoveryService,
} from "@/features/auth/services/auth.service";
import { getAccessToken, clearTokens } from "@/api/client";

interface AuthContextValue {
  user: User | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  impersonating: boolean;
  login: (data: LoginRequest) => Promise<{ requires_2fa: boolean; temp_token: string | null }>;
  verify2fa: (data: Verify2faRequest) => Promise<void>;
  logout: () => Promise<void>;
  requestRecovery: (data: RecoveryRequest) => Promise<{ message: string; token?: string }>;
  confirmRecovery: (data: RecoveryConfirmRequest) => Promise<{ message: string }>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const setSession = useCallback(
    (userData: User) => {
      setUser(userData);
      setPermissions(userData.permisos ?? []);
    },
    [],
  );

  const clearSession = useCallback(() => {
    setUser(null);
    setPermissions([]);
  }, []);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    getMeService()
      .then((userData) => {
        setSession(userData);
      })
      .catch(() => {
        clearSession();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [setSession, clearSession]);

  const login = useCallback(
    async (data: LoginRequest) => {
      const result = await loginService(data);
      if (!result.requires_2fa && result.access_token) {
        const userData = await getMeService();
        setSession(userData);
        navigate("/dashboard", { replace: true });
      }
      return { requires_2fa: result.requires_2fa, temp_token: result.temp_token };
    },
    [navigate, setSession],
  );

  const verify2fa = useCallback(
    async (data: Verify2faRequest) => {
      await verify2faSvc(data);
      const userData = await getMeService();
      setSession(userData);
      navigate("/dashboard", { replace: true });
    },
    [navigate, setSession],
  );

  const logout = useCallback(async () => {
    clearSession();
    clearTokens();
    navigate("/login", { replace: true });
  }, [navigate, clearSession]);

  const requestRecovery = useCallback(async (data: RecoveryRequest) => {
    const result = await requestRecoveryService(data);
    return { message: result.detail, token: result.token };
  }, []);

  const confirmRecovery = useCallback(async (data: RecoveryConfirmRequest) => {
    const result = await confirmRecoveryService(data);
    return { message: result.detail };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        permissions,
        isAuthenticated: user !== null,
        isLoading,
        impersonating: false,
        login,
        verify2fa,
        logout,
        requestRecovery,
        confirmRecovery,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }
  return context;
}

export default AuthContext;
