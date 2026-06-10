import { type VariantProps, cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-xs rounded font-label-md text-label-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-on-primary hover:opacity-90",
        secondary:
          "bg-white text-on-surface border border-outline-variant hover:bg-surface-container",
        ghost: "text-secondary hover:bg-surface-container hover:text-on-surface",
        danger: "bg-error text-on-error hover:opacity-90",
      },
      size: {
        sm: "h-8 px-sm py-xs",
        md: "h-10 px-md py-sm",
        lg: "h-12 px-lg py-md",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;

type ButtonProps = {
  variant?: ButtonVariants["variant"];
  size?: ButtonVariants["size"];
} & React.ComponentPropsWithoutRef<"button">;

export function Button({
  className,
  variant,
  size,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    >
      {children}
    </button>
  );
}
