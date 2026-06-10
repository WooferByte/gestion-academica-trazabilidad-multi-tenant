import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

type ToastVariant = "success" | "error" | "warning" | "info";

type ToastData = {
  id: string;
  message: string;
  variant: ToastVariant;
};

type ToastProps = ToastData & {
  onDismiss: (id: string) => void;
  duration?: number;
};

const variantStyles: Record<ToastVariant, string> = {
  success:
    "border-l-4 border-l-green-500 bg-green-50 text-green-800",
  error: "border-l-4 border-l-error bg-error-container text-on-error-container",
  warning:
    "border-l-4 border-l-yellow-500 bg-yellow-50 text-yellow-800",
  info: "border-l-4 border-l-secondary bg-secondary-container text-on-secondary-container",
};

function ToastItem({
  id,
  message,
  variant,
  onDismiss,
  duration = 5000,
}: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  return (
    <div
      className={cn(
        "flex items-center gap-sm rounded bg-white px-md py-sm shadow-lg font-body-md text-body-md",
        variantStyles[variant],
      )}
      role="alert"
    >
      <span className="flex-1">{message}</span>
      <button
        onClick={() => onDismiss(id)}
        className="text-current opacity-60 hover:opacity-100 transition-opacity"
      >
        <span className="material-symbols-outlined text-[18px]">close</span>
      </button>
    </div>
  );
}

let toastIdCounter = 0;

let globalToastFn: ((message: string, variant?: ToastVariant) => void) | null =
  null;

export function showToast(message: string, variant: ToastVariant = "info") {
  globalToastFn?.(message, variant);
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  globalToastFn = (message: string, variant: ToastVariant = "info") => {
    const id = `toast-${++toastIdCounter}`;
    setToasts((prev) => [...prev, { id, message, variant }]);
  };

  const dismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-lg right-lg z-50 flex flex-col gap-sm">
      {toasts.map((t) => (
        <ToastItem key={t.id} {...t} onDismiss={dismiss} />
      ))}
    </div>
  );
}
