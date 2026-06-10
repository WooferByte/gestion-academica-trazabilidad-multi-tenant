import { cn } from "@/lib/utils";

type CardProps = {
  children: React.ReactNode;
  className?: string;
} & React.ComponentPropsWithoutRef<"div">;

export function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-outline-variant bg-white",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
