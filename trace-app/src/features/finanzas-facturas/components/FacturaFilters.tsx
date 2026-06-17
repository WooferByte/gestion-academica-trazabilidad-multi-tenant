import { FilterBar } from "@/features/admin-estructura/shared/FilterBar";
import type { FilterConfig } from "@/features/admin-estructura/shared/FilterBar";

const ESTADOS = [
  { label: "Pendiente", value: "pendiente" },
  { label: "Abonada", value: "abonada" },
];

type FacturaFiltersProps = {
  values: Record<string, string>;
  onChange: (values: Record<string, string>) => void;
};

export function FacturaFilters({ values, onChange }: FacturaFiltersProps) {
  const filters: FilterConfig[] = [
    { key: "periodo", label: "Período", type: "text" },
    {
      key: "estado",
      label: "Estado",
      type: "select",
      options: ESTADOS,
    },
  ];

  return <FilterBar filters={filters} onFilter={onChange} values={values} />;
}
