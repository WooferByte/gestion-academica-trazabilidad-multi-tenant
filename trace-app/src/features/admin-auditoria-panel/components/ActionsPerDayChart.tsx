import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import type { ActionsPerDay } from "@/features/admin-auditoria-panel/types/auditoria";

type ActionsPerDayChartProps = {
  data?: ActionsPerDay[];
  isLoading: boolean;
};

export function ActionsPerDayChart({ data, isLoading }: ActionsPerDayChartProps) {
  if (isLoading) {
    return (
      <Card className="p-6">
        <Skeleton className="h-5 w-48 mb-4" />
        <Skeleton className="h-64 w-full" />
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="font-label-md text-label-md text-on-surface mb-4">Acciones por Día</h3>
        <p className="text-body-md text-on-surface-variant text-center py-16">
          No hay datos disponibles
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-label-md text-label-md text-on-surface mb-4">Acciones por Día</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-outline-variant)" />
          <XAxis
            dataKey="fecha"
            tick={{ fontSize: 12 }}
            stroke="var(--color-on-surface-variant)"
          />
          <YAxis tick={{ fontSize: 12 }} stroke="var(--color-on-surface-variant)" />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="total"
            stroke="var(--color-primary)"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Total acciones"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
