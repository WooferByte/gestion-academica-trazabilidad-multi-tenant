import { FilterBar } from "@/features/admin-estructura/shared/FilterBar";
import type { FilterConfig } from "@/features/admin-estructura/shared/FilterBar";

const filterConfigs: FilterConfig[] = [
  { key: "cohorte_id", label: "Cohorte", type: "text" },
  { key: "periodo", label: "Período", type: "text" },
  { key: "usuario_id", label: "Usuario", type: "text" },
];

type LiquidacionFiltersProps = {
  values: Record<string, string>;
  onChange: (values: Record<string, string>) => void;
};

export function LiquidacionFilters({ values, onChange }: LiquidacionFiltersProps) {
  return <FilterBar filters={filterConfigs} onFilter={onChange} values={values} />;
}
