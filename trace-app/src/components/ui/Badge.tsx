import { type VariantProps, cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-sm py-xs font-label-sm text-label-sm font-bold",
  {
    variants: {
      variant: {
        default: "bg-surface-container-high text-on-surface",
        success: "bg-green-100 text-green-800",
        warning: "bg-yellow-100 text-yellow-800",
        error: "bg-red-100 text-red-800",
        info: "bg-secondary-container text-on-secondary-container",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

type BadgeVariants = VariantProps<typeof badgeVariants>;

type BadgeProps = {
  variant?: BadgeVariants["variant"];
  children: React.ReactNode;
  className?: string;
};

export function Badge({ className, variant, children }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {children}
    </span>
  );
}
