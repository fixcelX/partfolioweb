import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  { label?: string } & React.InputHTMLAttributes<HTMLInputElement>
>(({ label, className, ...props }, ref) => (
  <label className="block">
    {label && (
      <span className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </span>
    )}
    <input
      ref={ref}
      className={cn(
        "h-11 w-full rounded-xl border border-gray-200 px-3 text-sm outline-none",
        "focus:border-primary focus:ring-2 focus:ring-primary/20",
        "dark:border-gray-700 dark:bg-gray-800",
        className,
      )}
      {...props}
    />
  </label>
));
Input.displayName = "Input";
