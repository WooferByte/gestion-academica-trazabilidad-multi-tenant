import { cn } from "@/lib/utils";

type AvatarProps = {
  src?: string;
  alt?: string;
  initials?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
};

const sizeClasses = {
  sm: "h-8 w-8 text-label-md",
  md: "h-10 w-10 text-body-md",
  lg: "h-12 w-12 text-headline-sm",
};

export function Avatar({
  src,
  alt,
  initials,
  size = "md",
  className,
}: AvatarProps) {
  if (src) {
    return (
      <div
        className={cn(
          "overflow-hidden rounded-full border border-outline-variant",
          sizeClasses[size],
          className,
        )}
      >
        <img
          src={src}
          alt={alt ?? ""}
          className="h-full w-full object-cover"
        />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-full bg-primary-fixed font-bold text-on-primary-fixed",
        sizeClasses[size],
        className,
      )}
    >
      {initials ?? "?"}
    </div>
  );
}
