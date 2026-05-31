import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

export function RatingStars({
  value,
  size = 14,
  className,
}: {
  value: number;
  size?: number;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-0.5", className)}>
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          width={size}
          height={size}
          className={
            i <= Math.round(value)
              ? "fill-warning text-warning"
              : "fill-gray-200 text-gray-200 dark:fill-gray-700 dark:text-gray-700"
          }
        />
      ))}
    </div>
  );
}
