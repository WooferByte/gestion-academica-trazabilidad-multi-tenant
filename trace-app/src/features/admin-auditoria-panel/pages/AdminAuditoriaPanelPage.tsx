import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader, EmptyState } from "@/features/admin-estructura/shared";
import api from "@/api/client";
import {
  useActionsPerDay,
  useCommsStatus,
  useInteractions,
  useLastActions,
} from "@/features/admin-auditoria-panel/hooks/useAuditoriaPanel";
import { ActionsPerDayChart } from "@/features/admin-auditoria-panel/components/ActionsPerDayChart";
import { CommsStatusChart } from "@/features/admin-auditoria-panel/components/CommsStatusChart";
import { InteractionsTable } from "@/features/admin-auditoria-panel/components/InteractionsTable";
import { LastActionsLog } from "@/features/admin-auditoria-panel/components/LastActionsLog";

export default function AdminAuditoriaPanelPage() {
  // Load users and materias for name lookup
  const { data: usuarios } = useQuery({
    queryKey: ["usuarios", "all"],
    queryFn: () => api.get<{ items: Array<{ id: string; nombre: string; apellido: string }> }>("/admin/usuarios").then((r) => r.data.items),
    staleTime: 5 * 60 * 1000,
  });

  const { data: materias } = useQuery({
    queryKey: ["materias", "all"],
    queryFn: () => api.get<{ items: Array<{ id: string; nombre: string }> }>("/admin/materias").then((r) => r.data.items),
    staleTime: 5 * 60 * 1000,
  });

  const userMap = useMemo(() => {
    const map: Record<string, string> = {};
    usuarios?.forEach((u) => { map[u.id] = `${u.nombre} ${u.apellido}`.trim(); });
    return map;
  }, [usuarios]);

  const materiaMap = useMemo(() => {
    const map: Record<string, string> = {};
    materias?.forEach((m) => { map[m.id] = m.nombre; });
    return map;
  }, [materias]);

  const panelFilters = { limit: "200" };

  const { data: actionsPerDay, isLoading: loadingActions } = useActionsPerDay(panelFilters);
  const { data: commsStatus, isLoading: loadingComms } = useCommsStatus(panelFilters);
  const { data: interactions, isLoading: loadingInteractions } = useInteractions(panelFilters);
  const { data: lastActions, isLoading: loadingLastActions } = useLastActions(panelFilters);

  // Enhance data with user/materia names
  const enhancedInteractions = useMemo(() => {
    if (!interactions) return undefined;
    return interactions.map((item) => ({
      ...item,
      usuario_nombre: userMap[item.usuario_id] ?? item.usuario_id.slice(0, 8) + "...",
      materia_nombre: item.materia_id ? (materiaMap[item.materia_id] ?? item.materia_id.slice(0, 8) + "...") : "-",
    }));
  }, [interactions, userMap, materiaMap]);

  const enhancedLastActions = useMemo(() => {
    if (!lastActions) return undefined;
    return lastActions.map((item) => ({
      ...item,
      usuario_nombre: userMap[item.actor_id] ?? item.actor_id.slice(0, 8) + "...",
      detalle_texto: item.detalle
        ? typeof item.detalle === "object"
          ? Object.values(item.detalle)
              .flatMap((v) => (Array.isArray(v) ? v : [v]))
              .filter((v) => {
                if (v === null || v === undefined) return false;
                const s = String(v).trim();
                if (s === "" || s === "None" || s === "[object Object]") return false;
                // Filter out UUIDs (36 chars with hyphens)
                if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s)) return false;
                // Filter out long hex strings
                if (s.length > 30 && /^[0-9a-f]+$/i.test(s.replace(/-/g, ""))) return false;
                return true;
              })
              .map((v) => String(v))
              .join(", ")
          : String(item.detalle)
        : "-",
    }));
  }, [lastActions, userMap]);

  const hasData = (loadingActions && loadingComms && loadingInteractions && loadingLastActions) === false
    && (actionsPerDay && actionsPerDay.length > 0)
    || (commsStatus && commsStatus.length > 0)
    || (interactions && interactions.length > 0)
    || (lastActions && lastActions.length > 0);

  return (
    <div className="flex flex-col gap-6 p-lg">
      <PageHeader title="Panel de Auditoría" />

      {!hasData ? (
        <EmptyState message="No hay datos de auditoría disponibles. Los datos se generan al usar el sistema." />
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ActionsPerDayChart data={actionsPerDay} isLoading={loadingActions} />
            <CommsStatusChart data={commsStatus} isLoading={loadingComms} />
          </div>
          <InteractionsTable data={enhancedInteractions} isLoading={loadingInteractions} />
          <LastActionsLog data={enhancedLastActions} isLoading={loadingLastActions} />
        </>
      )}
    </div>
  );
}
