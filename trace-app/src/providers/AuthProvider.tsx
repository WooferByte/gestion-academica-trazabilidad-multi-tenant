import { type ReactNode } from "react";
import { AuthProvider } from "@/features/auth/hooks/useAuth";

export function AppAuthProvider({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}
