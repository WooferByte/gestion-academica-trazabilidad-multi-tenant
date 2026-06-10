import { cn } from "@/lib/utils";

type SkeletonProps = {
  className?: string;
} & React.ComponentPropsWithoutRef<"div">;

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded bg-surface-container",
        className,
      )}
      {...props}
    />
  );
}
