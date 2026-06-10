import { Button } from "@/components/ui/Button";

type ImpersonationBannerProps = {
  impersonatedName?: string;
  onRevert?: () => void;
};

export function ImpersonationBanner({
  impersonatedName,
  onRevert,
}: ImpersonationBannerProps) {
  if (!impersonatedName) return null;

  return (
    <div className="flex items-center justify-between gap-md bg-yellow-100 px-lg py-sm">
      <div className="flex items-center gap-sm">
        <span className="material-symbols-outlined text-[18px] text-yellow-800">
          warning
        </span>
        <p className="font-body-md text-body-md text-yellow-800">
          MODO ADMINISTRADOR: Estás operando como {impersonatedName}
        </p>
      </div>
      {onRevert && (
        <Button variant="ghost" size="sm" onClick={onRevert}>
          Revertir
        </Button>
      )}
    </div>
  );
}
