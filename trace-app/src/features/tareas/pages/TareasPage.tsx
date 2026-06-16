import { useState } from "react";
import { useAuth } from "@/features/auth/hooks/useAuth";
import MisTareasListPage from "./MisTareasListPage";
import TareasAdminPage from "./TareasAdminPage";

export default function TareasPage() {
  const { permissions } = useAuth();
  const isSuperAdmin = permissions.includes("equipos:asignar") || permissions.includes("rbac:gestionar");
  const canAdmin = permissions.includes("tareas:gestionar");
  const [view, setView] = useState<"mis-tareas" | "admin">("mis-tareas");

  if (canAdmin) {
    return (
      <div className="space-y-lg p-lg">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setView("mis-tareas")}
            className={`px-3 py-1 text-sm rounded-md ${
              view === "mis-tareas"
                ? "bg-primary text-primary-foreground"
                : "bg-accent text-accent-foreground"
            }`}
          >
            Mis Tareas
          </button>
          {isSuperAdmin && (
            <button
              type="button"
              onClick={() => setView("admin")}
              className={`px-3 py-1 text-sm rounded-md ${
                view === "admin"
                  ? "bg-primary text-primary-foreground"
                  : "bg-accent text-accent-foreground"
              }`}
            >
              Admin
            </button>
          )}
        </div>
        {view === "admin" ? <TareasAdminPage /> : <MisTareasListPage />}
      </div>
    );
  }

  return <MisTareasListPage />;
}
