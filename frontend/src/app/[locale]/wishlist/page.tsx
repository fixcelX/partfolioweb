"use client";

import { useEffect } from "react";
import { Heart } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { ProductGrid } from "@/components/product/product-grid";
import { useWishlist } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";

export default function WishlistPage() {
  const t = useTranslations("wishlist");
  const tCart = useTranslations("cart");
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const hydrated = useAuth((s) => s.hydrated);
  const { data: products, isLoading } = useWishlist(!!user);

  useEffect(() => {
    if (hydrated && !user) router.replace("/login?next=/wishlist");
  }, [hydrated, user, router]);

  if (!user) return null;

  return (
    <div className="container-zm py-8">
      <h1 className="mb-6 flex items-center gap-2 text-2xl font-extrabold">
        <Heart className="h-6 w-6 text-danger" /> {t("title")}
      </h1>

      {isLoading ? (
        <ProductGrid loading skeletonCount={10} />
      ) : !products || products.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
          <Heart className="h-20 w-20 text-gray-200" />
          <h2 className="text-xl font-bold">{t("empty")}</h2>
          <p className="text-gray-500">{t("emptyText")}</p>
          <Link href="/catalog">
            <Button size="lg">{tCart("goShopping")}</Button>
          </Link>
        </div>
      ) : (
        <ProductGrid products={products} />
      )}
    </div>
  );
}
