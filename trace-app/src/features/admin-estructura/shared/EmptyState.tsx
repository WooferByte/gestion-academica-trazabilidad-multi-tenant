import { Inbox } from "lucide-react";
import { cn } from "@/lib/utils";

type EmptyStateProps = {
  icon?: React.ReactNode;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
};

export function EmptyState({ icon, message, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 text-center", className)}>
      <div className="mb-4 text-secondary">{icon ?? <Inbox className="size-12" />}</div>
      <p className="mb-4 text-body-md text-on-surface-variant">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="font-label-md text-label-md text-primary hover:underline"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
