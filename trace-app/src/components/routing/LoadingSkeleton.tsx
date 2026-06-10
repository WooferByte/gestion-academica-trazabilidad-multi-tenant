import { Skeleton } from "@/components/ui/Skeleton";

export function LoadingSkeleton() {
  return (
    <div className="flex h-screen flex-col gap-md bg-background p-lg">
      <div className="flex items-center gap-md">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid grid-cols-3 gap-md">
        <Skeleton className="h-32 rounded-xl" />
        <Skeleton className="h-32 rounded-xl" />
        <Skeleton className="h-32 rounded-xl" />
      </div>
      <Skeleton className="h-64 w-full rounded-xl" />
    </div>
  );
}

export default LoadingSkeleton;
