"use client";

import { Heart } from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";
import { useToast } from "@/components/ui/toast";
import { useToggleWishlist, useWishlist } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";
import { cn } from "@/lib/utils";
import type { Product } from "@/lib/types";

export function WishlistButton({
  productId,
  product,
  variant = "icon",
  className,
}: {
  productId: number;
  product?: Product;
  variant?: "icon" | "full";
  className?: string;
}) {
  const t = useTranslations("product");
  const tw = useTranslations("wishlist");
  const router = useRouter();
  const toast = useToast();
  const user = useAuth((s) => s.user);
  const { data: wishlist } = useWishlist(!!user);
  const toggle = useToggleWishlist();

  const active = !!wishlist?.some((p) => p.id === productId);

  const onClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) {
      router.push("/login?next=/wishlist");
      return;
    }
    toggle.mutate(
      { productId, active, product },
      {
        onSuccess: () => toast.push(active ? tw("removed") : tw("added")),
      },
    );
  };

  if (variant === "full") {
    return (
      <button
        onClick={onClick}
        disabled={toggle.isPending}
        className={cn(
          "inline-flex h-12 w-12 items-center justify-center rounded-xl border transition",
          active
            ? "border-danger bg-danger/10 text-danger"
            : "border-gray-300 text-gray-500 hover:border-danger hover:text-danger dark:border-gray-700",
          className,
        )}
        aria-label={active ? t("inWishlist") : t("addToWishlist")}
      >
        <Heart className={cn("h-5 w-5", active && "fill-danger")} />
      </button>
    );
  }

  return (
    <button
      onClick={onClick}
      disabled={toggle.isPending}
      className={cn(
        "absolute right-2 top-2 z-10 grid h-9 w-9 place-items-center rounded-full bg-white/90 shadow-sm backdrop-blur transition hover:scale-110 dark:bg-gray-900/90",
        className,
      )}
      aria-label={active ? t("inWishlist") : t("addToWishlist")}
    >
      <Heart
        className={cn(
          "h-4 w-4 transition",
          active ? "fill-danger text-danger" : "text-gray-500",
        )}
      />
    </button>
  );
}
