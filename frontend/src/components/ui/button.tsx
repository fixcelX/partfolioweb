import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "outline" | "ghost" | "danger";
type Size = "sm" | "md" | "lg" | "icon";

const variants: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-primary-600 active:bg-primary-700 shadow-sm",
  outline:
    "border border-gray-300 bg-white text-gray-900 hover:bg-gray-50 dark:bg-transparent dark:text-gray-100 dark:border-gray-700 dark:hover:bg-gray-800",
  ghost: "text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800",
  danger: "bg-danger text-white hover:bg-red-700",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-7 text-base",
  icon: "h-10 w-10",
};

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant = "primary", size = "md", loading = false, disabled, children, ...props },
    ref,
  ) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      aria-busy={loading}
      className={cn(
        "relative inline-flex items-center justify-center gap-2 rounded-xl font-semibold",
        "transition-all duration-150 focus-visible:outline-none focus-visible:ring-2",
        "focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50",
        "active:scale-[0.97] disabled:pointer-events-none",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";
