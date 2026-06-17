import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { useAuth } from "@/features/auth/hooks/useAuth";

export function DashboardPage() {
  const { user } = useAuth();

  const { data: alumnos } = useQuery({
    queryKey: ["dashboard", "alumnos"],
    queryFn: () =>
      api
        .get<{ items: unknown[]; total: number }>("/admin/usuarios", {
          params: { rol: "ALUMNO" },
        })
        .then((r) => r.data.total ?? r.data.items?.length ?? 0)
        .catch(() => 0),
    staleTime: 60 * 1000,
  });

  const { data: materias } = useQuery({
    queryKey: ["dashboard", "materias"],
    queryFn: () =>
      api
        .get<{ items: unknown[]; total: number }>("/admin/materias")
        .then((r) => r.data.total ?? r.data.items?.length ?? 0)
        .catch(() => 0),
    staleTime: 60 * 1000,
  });

  const { data: encuentros } = useQuery({
    queryKey: ["dashboard", "encuentros"],
    queryFn: () =>
      api
        .get<unknown[]>("/encuentros/slots")
        .then((r) => (Array.isArray(r.data) ? r.data.length : 0))
        .catch(() => 0),
    staleTime: 60 * 1000,
  });

  const { data: atrasados } = useQuery({
    queryKey: ["dashboard", "atrasados"],
    queryFn: () =>
      api
        .get<{ total?: number; items?: unknown[] }>("/analisis/atrasados")
        .then((r) => r.data?.total ?? (Array.isArray(r.data) ? r.data.length : 0))
        .catch(() => 0),
    staleTime: 60 * 1000,
  });

  return (
    <div className="flex flex-col gap-lg p-lg">
      <div>
        <h1 className="font-headline-lg text-headline-lg text-on-surface">
          Panel de Control General
        </h1>
        {user && (
          <p className="mt-sm font-body-lg text-body-lg text-secondary">
            Bienvenido, {user.nombre} {user.apellido}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-md md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Alumnos" value={String(alumnos ?? "—")} icon="people" />
        <StatCard title="Materias" value={String(materias ?? "—")} icon="menu_book" />
        <StatCard title="Encuentros" value={String(encuentros ?? "—")} icon="calendar_month" />
        <StatCard title="Atrasados" value={String(atrasados ?? "—")} icon="warning" />
      </div>
    </div>
  );
}

type StatCardProps = {
  title: string;
  value: string;
  icon: string;
};

function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div className="flex items-center gap-md rounded-xl border border-outline-variant bg-white p-md">
      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-fixed text-on-primary-fixed">
        <span className="material-symbols-outlined text-[24px]">{icon}</span>
      </div>
      <div>
        <p className="font-label-sm text-label-sm text-secondary">{title}</p>
        <p className="font-headline-sm text-headline-sm text-on-surface">
          {value}
        </p>
      </div>
    </div>
  );
}

export default DashboardPage;
