import { Avatar } from "@/components/ui/Avatar";
import { useAuth } from "@/features/auth/hooks/useAuth";

export function Topbar() {
  const { user } = useAuth();

  const initials =
    user?.nombre && user?.apellido
      ? `${user.nombre[0]}${user.apellido[0]}`.toUpperCase()
      : user?.email?.[0]?.toUpperCase() ?? "?";

  return (
    <header className="flex h-16 items-center justify-between border-b border-outline-variant bg-white px-lg">
      {/* Search */}
      <div className="relative w-80">
        <span className="material-symbols-outlined absolute left-sm top-1/2 -translate-y-1/2 text-[18px] text-secondary">
          search
        </span>
        <input
          type="text"
          placeholder="Buscar estudiante, factura o acta..."
          className="h-10 w-full rounded-full border border-outline-variant bg-surface-container-low pl-xl pr-md font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary transition-colors"
        />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-md">
        {/* Tenant selector placeholder */}
        <button className="flex items-center gap-xs rounded px-sm py-xs text-secondary hover:text-on-surface transition-colors">
          <span className="material-symbols-outlined text-[18px]">
            apartment
          </span>
          <span className="font-body-md text-body-md">Tenant</span>
        </button>

        {/* Notifications */}
        <button
          className="relative rounded p-sm text-secondary hover:bg-surface-container hover:text-on-surface transition-colors"
          title="Notificaciones"
        >
          <span className="material-symbols-outlined text-[20px]">
            notifications
          </span>
          <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-error text-[9px] font-bold text-on-error">
            3
          </span>
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-sm">
          <Avatar initials={initials} size="sm" />
          <div className="flex flex-col">
            <span className="font-body-md text-body-md font-medium text-on-surface leading-tight">
              {user?.nombre ?? ""} {user?.apellido ?? ""}
            </span>
            <span className="font-label-sm text-label-sm text-secondary leading-tight">
              {user?.roles?.[0] ?? ""}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
