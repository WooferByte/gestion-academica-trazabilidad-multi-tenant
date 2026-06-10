import { cn } from "@/lib/utils";

type Tab = {
  id: string;
  label: string;
};

type ImportTabsProps = {
  tabs: Tab[];
  active: string;
  onChange: (id: string) => void;
};

export function ImportTabs({ tabs, active, onChange }: ImportTabsProps) {
  return (
    <div className="flex gap-xs border-b border-outline-variant">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            "border-b-2 px-lg py-sm font-label-md text-label-md transition-colors",
            active === tab.id
              ? "border-primary text-primary"
              : "border-transparent text-secondary hover:text-on-surface",
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
