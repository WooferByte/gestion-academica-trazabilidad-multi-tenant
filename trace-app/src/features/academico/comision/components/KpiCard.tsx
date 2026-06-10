import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { cn } from "@/lib/utils";

type KpiCardProps = {
  title: string;
  value: number | null | undefined;
  icon: string;
  loading?: boolean;
  className?: string;
};

export function KpiCard({ title, value, icon, loading, className }: KpiCardProps) {
  return (
    <Card className={cn("flex items-center gap-md p-lg", className)}>
      <span className="material-symbols-outlined text-3xl text-secondary">
        {icon}
      </span>
      <div className="flex flex-col">
        <span className="font-body-sm text-body-sm text-on-surface-variant">
          {title}
        </span>
        {loading ? (
          <Skeleton className="mt-xs h-8 w-20" />
        ) : (
          <span className="font-headline-md text-headline-md text-on-surface">
            {value != null ? value : "—"}
          </span>
        )}
      </div>
    </Card>
  );
}
