import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

type DialogProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
};

export function Dialog({
  open,
  onClose,
  title,
  children,
  footer,
  className,
}: DialogProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div
        className={cn(
          "mx-lg w-full max-w-lg rounded-xl bg-white shadow-lg",
          className,
        )}
      >
        {title && (
          <div className="flex items-center justify-between border-b border-outline-variant px-lg py-md">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-secondary hover:text-on-surface transition-colors"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        )}
        <div className="px-lg py-md">{children}</div>
        {footer && (
          <div className="flex items-center justify-end gap-sm border-t border-outline-variant px-lg py-md">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
