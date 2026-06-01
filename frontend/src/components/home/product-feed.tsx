"use client";

import { useProductFeed } from "@/lib/hooks";
import { ProductGrid } from "@/components/product/product-grid";

export function ProductFeed({
  kind,
  title,
  accent,
}: {
  kind: "featured" | "new" | "bestsellers";
  title: string;
  accent?: string;
}) {
  const { data, isLoading } = useProductFeed(kind);
  if (!isLoading && (!data || data.length === 0)) return null;
  return (
    <section className="container-zm mt-10">
      <div className="mb-4 flex items-center gap-3">
        <span
          className="h-6 w-1.5 rounded-full bg-primary"
          style={accent ? { background: accent } : undefined}
        />
        <h2 className="text-xl font-extrabold sm:text-2xl">{title}</h2>
      </div>
      <ProductGrid products={data?.slice(0, 10)} loading={isLoading} skeletonCount={5} />
    </section>
  );
}
