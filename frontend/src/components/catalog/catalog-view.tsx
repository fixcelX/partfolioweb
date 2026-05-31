"use client";

import { useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { ProductGrid } from "@/components/product/product-grid";
import { Button } from "@/components/ui/button";
import { useBrands, useCategories, useProducts } from "@/lib/hooks";
import { cn } from "@/lib/utils";

interface Filters {
  category?: string;
  min_price?: string;
  max_price?: string;
  brand?: string;
  rating?: string;
  in_stock?: string;
  ordering: string;
  page: number;
}

export function CatalogView({
  categorySlug,
  title,
  search,
}: {
  categorySlug?: string;
  title: string;
  search?: string;
}) {
  const t = useTranslations("catalog");
  const { data: brands } = useBrands();
  const { data: categories } = useCategories();
  const [filters, setFilters] = useState<Filters>({ ordering: "-created_at", page: 1 });
  const [draft, setDraft] = useState<{ min: string; max: string }>({ min: "", max: "" });
  const [mobileOpen, setMobileOpen] = useState(false);

  // Kategoriya sahifasida slug fiksatsiya, aks holda filtrdan
  const effectiveCategory = categorySlug ?? filters.category;

  const { data, isLoading } = useProducts({
    category: effectiveCategory,
    search,
    min_price: filters.min_price,
    max_price: filters.max_price,
    brand: filters.brand,
    rating: filters.rating,
    in_stock: filters.in_stock,
    ordering: filters.ordering,
    page: filters.page,
  });

  const set = (patch: Partial<Filters>) =>
    setFilters((f) => ({ ...f, ...patch, page: 1 }));

  const reset = () => {
    setFilters({ ordering: "-created_at", page: 1 });
    setDraft({ min: "", max: "" });
  };

  const activeCount =
    (filters.brand ? 1 : 0) +
    (filters.rating ? 1 : 0) +
    (filters.in_stock ? 1 : 0) +
    (filters.min_price || filters.max_price ? 1 : 0) +
    (!categorySlug && filters.category ? 1 : 0);

  const FilterPanel = (
    <div className="space-y-6">
      {/* Kategoriya (faqat umumiy katalog/qidiruvda) */}
      {!categorySlug && categories && categories.length > 0 && (
        <div>
          <h4 className="mb-2 font-bold">{t("category")}</h4>
          <div className="max-h-56 space-y-1 overflow-y-auto pr-1">
            {categories.map((root) =>
              root.children.length > 0 ? (
                root.children.map((c) => (
                  <button
                    key={c.id}
                    onClick={() =>
                      set({ category: filters.category === c.slug ? undefined : c.slug })
                    }
                    className={cn(
                      "block w-full rounded-lg px-2 py-1.5 text-left text-sm transition",
                      filters.category === c.slug
                        ? "bg-primary-50 font-semibold text-primary dark:bg-primary-900/30"
                        : "text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800",
                    )}
                  >
                    {c.name}
                  </button>
                ))
              ) : (
                <button
                  key={root.id}
                  onClick={() =>
                    set({ category: filters.category === root.slug ? undefined : root.slug })
                  }
                  className={cn(
                    "block w-full rounded-lg px-2 py-1.5 text-left text-sm transition",
                    filters.category === root.slug
                      ? "bg-primary-50 font-semibold text-primary dark:bg-primary-900/30"
                      : "text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800",
                  )}
                >
                  {root.name}
                </button>
              ),
            )}
          </div>
        </div>
      )}

      {/* Narx */}
      <div>
        <h4 className="mb-2 font-bold">{t("price")}</h4>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder={t("from")}
            value={draft.min}
            onChange={(e) => setDraft((d) => ({ ...d, min: e.target.value }))}
            className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm dark:border-gray-700 dark:bg-gray-800"
          />
          <span className="text-gray-400">—</span>
          <input
            type="number"
            placeholder={t("to")}
            value={draft.max}
            onChange={(e) => setDraft((d) => ({ ...d, max: e.target.value }))}
            className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm dark:border-gray-700 dark:bg-gray-800"
          />
        </div>
        <Button
          size="sm"
          variant="outline"
          className="mt-2 w-full"
          onClick={() => set({ min_price: draft.min, max_price: draft.max })}
        >
          {t("apply")}
        </Button>
      </div>

      {/* Brend */}
      {brands && brands.length > 0 && (
        <div>
          <h4 className="mb-2 font-bold">{t("brand")}</h4>
          <div className="flex flex-wrap gap-2">
            {brands.map((b) => (
              <button
                key={b.id}
                onClick={() => set({ brand: filters.brand === b.slug ? undefined : b.slug })}
                className={cn(
                  "rounded-lg border px-2.5 py-1 text-xs font-medium transition",
                  filters.brand === b.slug
                    ? "border-primary bg-primary text-white"
                    : "border-gray-200 text-gray-600 hover:border-primary dark:border-gray-700 dark:text-gray-300",
                )}
              >
                {b.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Reyting */}
      <div>
        <h4 className="mb-2 font-bold">{t("rating")}</h4>
        {[5, 4, 3].map((r) => (
          <label key={r} className="flex cursor-pointer items-center gap-2 py-1 text-sm">
            <input
              type="radio"
              name="rating"
              checked={filters.rating === String(r)}
              onChange={() => set({ rating: String(r) })}
              className="accent-primary"
            />
            {r}★ {t("andUp")}
          </label>
        ))}
      </div>

      <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
        <input
          type="checkbox"
          checked={filters.in_stock === "true"}
          onChange={(e) => set({ in_stock: e.target.checked ? "true" : undefined })}
          className="accent-primary"
        />
        {t("inStockOnly")}
      </label>

      {activeCount > 0 && (
        <Button variant="ghost" size="sm" className="w-full" onClick={reset}>
          <X className="h-4 w-4" /> {t("reset")} ({activeCount})
        </Button>
      )}
    </div>
  );

  return (
    <div className="container-zm py-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold">{title}</h1>
        <div className="flex items-center gap-2">
          <select
            value={filters.ordering}
            onChange={(e) => set({ ordering: e.target.value })}
            className="h-10 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <option value="-created_at">{t("sortNew")}</option>
            <option value="price">{t("sortPriceAsc")}</option>
            <option value="-price">{t("sortPriceDesc")}</option>
            <option value="-rating">{t("sortRating")}</option>
            <option value="-sold_count">{t("sortPopular")}</option>
          </select>
          <Button variant="outline" size="sm" className="relative lg:hidden" onClick={() => setMobileOpen(true)}>
            <SlidersHorizontal className="h-4 w-4" /> {t("filters")}
            {activeCount > 0 && (
              <span className="absolute -right-1 -top-1 grid h-5 w-5 place-items-center rounded-full bg-primary text-[11px] text-white">
                {activeCount}
              </span>
            )}
          </Button>
        </div>
      </div>

      {data && (
        <p className="mb-4 text-sm text-gray-500">{t("found", { count: data.count })}</p>
      )}

      <div className="flex gap-6">
        <aside className="hidden w-64 shrink-0 lg:block">
          <div className="sticky top-20 rounded-2xl border border-gray-100 p-5 dark:border-gray-800">
            <h3 className="mb-4 flex items-center gap-2 font-bold">
              <SlidersHorizontal className="h-4 w-4" /> {t("filters")}
            </h3>
            {FilterPanel}
          </div>
        </aside>

        <div className="flex-1">
          {!isLoading && data?.results.length === 0 ? (
            <div className="grid place-items-center rounded-2xl border border-dashed border-gray-200 py-20 text-gray-500 dark:border-gray-700">
              {t("empty")}
            </div>
          ) : (
            <ProductGrid products={data?.results} loading={isLoading} />
          )}

          {data && data.total_pages > 1 && (
            <div className="mt-8 flex justify-center gap-2">
              {Array.from({ length: data.total_pages }).slice(0, 8).map((_, i) => (
                <button
                  key={i}
                  onClick={() => setFilters((f) => ({ ...f, page: i + 1 }))}
                  className={`h-10 w-10 rounded-xl text-sm font-semibold transition ${
                    data.current_page === i + 1
                      ? "bg-primary text-white"
                      : "border border-gray-200 hover:border-primary dark:border-gray-700"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Mobil filtr drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <div className="absolute bottom-0 left-0 right-0 max-h-[85vh] overflow-y-auto rounded-t-3xl bg-white p-6 dark:bg-gray-950">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-bold">{t("filters")}</h3>
              <button onClick={() => setMobileOpen(false)}><X className="h-5 w-5" /></button>
            </div>
            {FilterPanel}
            <Button className="mt-4 w-full" onClick={() => setMobileOpen(false)}>{t("apply")}</Button>
          </div>
        </div>
      )}
    </div>
  );
}
