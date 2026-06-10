import { useAuth } from "@/features/auth/hooks/useAuth";

export function DashboardPage() {
  const { user } = useAuth();

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
        <StatCard title="Alumnos" value="—" icon="people" />
        <StatCard title="Materias" value="—" icon="menu_book" />
        <StatCard title="Encuentros" value="—" icon="calendar_month" />
        <StatCard title="Atrasados" value="—" icon="warning" />
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
