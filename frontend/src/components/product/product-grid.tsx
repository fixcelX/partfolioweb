import { ProductCardSkeleton } from "@/components/ui/skeleton";
import type { Product } from "@/lib/types";
import { ProductCard } from "./product-card";

export function ProductGrid({
  products,
  loading,
  skeletonCount = 10,
}: {
  products?: Product[];
  loading?: boolean;
  skeletonCount?: number;
}) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
      </div>
    );
  }
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {products?.map((p) => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  );
}
