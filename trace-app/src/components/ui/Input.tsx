import { forwardRef } from "react";
import { cn } from "@/lib/utils";

type InputProps = {
  label?: string;
  error?: string;
} & React.ComponentPropsWithoutRef<"input">;

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="flex flex-col gap-xs">
        {label && (
          <label
            htmlFor={inputId}
            className="font-label-md text-label-md text-on-surface"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "h-10 w-full rounded border bg-white px-md py-sm font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant transition-colors focus:outline-none focus:ring-2 focus:ring-primary",
            error
              ? "border-error focus:ring-error"
              : "border-outline-variant",
            className,
          )}
          {...props}
        />
        {error && (
          <p className="font-label-sm text-label-sm text-error">{error}</p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";
