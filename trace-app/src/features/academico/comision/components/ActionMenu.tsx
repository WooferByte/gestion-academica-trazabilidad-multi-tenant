import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { Card } from "@/components/ui/Card";

interface ActionItem {
  label: string;
  icon: string;
  path: string;
  permission?: string;
}

const ACTIONS: ActionItem[] = [
  { label: "Importar calificaciones", icon: "upload_file", path: "importar", permission: "calificaciones:importar" },
  { label: "Configurar umbral", icon: "tune", path: "umbral", permission: "calificaciones:importar" },
  { label: "Ver atrasados", icon: "warning", path: "atrasados", permission: "atrasados:ver" },
  { label: "Ranking", icon: "leaderboard", path: "ranking", permission: "atrasados:ver" },
  { label: "Notas finales", icon: "assignment", path: "notas", permission: "atrasados:ver" },
  { label: "TPs sin corregir", icon: "description", path: "tps-sin-corregir", permission: "atrasados:ver" },
  { label: "Comunicar", icon: "mail", path: "comunicar", permission: "comunicacion:enviar" },
  { label: "Monitor", icon: "monitoring", path: "monitor", permission: "atrasados:ver" },
];

export function ActionMenu() {
  const navigate = useNavigate();
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const { permissions } = useAuth();

  const visible = ACTIONS.filter(
    (a) => !a.permission || permissions.includes(a.permission),
  );

  return (
    <Card className="p-lg">
      <h3 className="mb-md font-label-lg text-label-lg text-on-surface">Acciones</h3>
      <div className="grid grid-cols-2 gap-md sm:grid-cols-3 md:grid-cols-4">
        {visible.map((action) => (
          <button
            key={action.path}
            onClick={() => navigate(`/academico/${materiaId}/${cohorteId}/${action.path}`)}
            className="flex flex-col items-center gap-sm rounded-xl border border-outline-variant bg-white p-md transition-colors hover:bg-surface-container"
          >
            <span className="material-symbols-outlined text-2xl text-secondary">
              {action.icon}
            </span>
            <span className="text-center font-label-sm text-label-sm text-on-surface">
              {action.label}
            </span>
          </button>
        ))}
      </div>
    </Card>
  );
}
