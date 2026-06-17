import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

type PageHeaderAction = {
  label: string;
  onClick: () => void;
};

type PageHeaderProps = {
  title: string;
  action?: PageHeaderAction;
  className?: string;
};

export function PageHeader({ title, action, className }: PageHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      <h1 className="font-headline-md text-headline-md text-on-surface">{title}</h1>
      {action && <Button onClick={action.onClick}>{action.label}</Button>}
    </div>
  );
}
