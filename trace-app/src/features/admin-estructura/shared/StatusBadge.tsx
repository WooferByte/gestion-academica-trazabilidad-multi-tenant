import { Badge } from "@/components/ui/Badge";

type StatusBadgeProps = {
  active: boolean;
  label?: string;
};

export function StatusBadge({ active, label }: StatusBadgeProps) {
  return <Badge variant={active ? "success" : "default"}>{label ?? (active ? "Activo" : "Inactivo")}</Badge>;
}
