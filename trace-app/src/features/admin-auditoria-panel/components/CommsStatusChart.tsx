import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import type { CommsStatus } from "@/features/admin-auditoria-panel/types/auditoria";

type CommsStatusChartProps = {
  data?: CommsStatus[];
  isLoading: boolean;
};

const STATUS_COLORS = {
  pendientes: "#F59E0B",
  enviadas: "#10B981",
  fallidas: "#EF4444",
};

export function CommsStatusChart({ data, isLoading }: CommsStatusChartProps) {
  if (isLoading) {
    return (
      <Card className="p-6">
        <Skeleton className="h-5 w-56 mb-4" />
        <Skeleton className="h-64 w-full" />
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="font-label-md text-label-md text-on-surface mb-4">
          Estado de Comunicaciones
        </h3>
        <p className="text-body-md text-on-surface-variant text-center py-16">
          No hay datos disponibles
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-label-md text-label-md text-on-surface mb-4">
        Estado de Comunicaciones
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-outline-variant)" />
          <XAxis
            dataKey="docente_email"
            tick={{ fontSize: 12 }}
            stroke="var(--color-on-surface-variant)"
          />
          <YAxis tick={{ fontSize: 12 }} stroke="var(--color-on-surface-variant)" />
          <Tooltip />
          <Legend />
          <Bar dataKey="pendientes" fill={STATUS_COLORS.pendientes} name="Pendientes" stackId="a" />
          <Bar dataKey="enviadas" fill={STATUS_COLORS.enviadas} name="Enviadas" stackId="a" />
          <Bar dataKey="fallidas" fill={STATUS_COLORS.fallidas} name="Fallidas" stackId="a" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
