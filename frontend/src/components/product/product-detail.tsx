"use client";

import { useState } from "react";
import Image from "next/image";
import { Minus, Plus, ShoppingCart, Truck } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { RatingStars } from "@/components/ui/rating-stars";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { ProductGrid } from "./product-grid";
import { WishlistButton } from "./wishlist-button";
import { ReviewForm } from "./review-form";
import { useAddToCart, useProduct, useReviews } from "@/lib/hooks";
import { formatSom } from "@/lib/utils";

export function ProductDetailView({ slug }: { slug: string }) {
  const t = useTranslations("product");
  const tc = useTranslations("common");
  const { data: product, isLoading } = useProduct(slug);
  const { data: reviews } = useReviews(slug);
  const add = useAddToCart();
  const toast = useToast();
  const [active, setActive] = useState(0);
  const [qty, setQty] = useState(1);
  const [tab, setTab] = useState<"desc" | "reviews">("desc");

  if (isLoading || !product) {
    return (
      <div className="container-zm grid gap-8 py-8 lg:grid-cols-2">
        <Skeleton className="aspect-square w-full rounded-2xl" />
        <div className="space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-10 w-1/2" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
    );
  }

  const images = product.images.length
    ? product.images
    : [{ id: 0, src: product.image ?? "", alt: product.name, order: 0 }];

  const onAdd = () => {
    add.mutate(
      { product_id: product.id, quantity: qty, product },
      {
        onSuccess: () => toast.push(t("added")),
        onError: () => toast.push(tc("error"), "error"),
      },
    );
  };

  return (
    <div className="container-zm py-6">
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Galereya */}
        <div className="flex flex-col-reverse gap-3 sm:flex-row">
          <div className="flex gap-2 sm:flex-col">
            {images.map((img, i) => (
              <button
                key={img.id}
                onClick={() => setActive(i)}
                className={`relative h-16 w-16 shrink-0 overflow-hidden rounded-xl border-2 ${
                  active === i ? "border-primary" : "border-transparent"
                }`}
              >
                {img.src && <Image src={img.src} alt={img.alt} fill className="object-cover" sizes="64px" />}
              </button>
            ))}
          </div>
          <div className="relative aspect-square flex-1 overflow-hidden rounded-2xl bg-gray-50 dark:bg-gray-800">
            {images[active]?.src && (
              <Image
                src={images[active].src}
                alt={product.name}
                fill
                priority
                sizes="(max-width:1024px) 100vw, 600px"
                className="object-cover"
              />
            )}
            {product.discount_percent > 0 && (
              <span className="absolute left-3 top-3 rounded-lg bg-danger px-2.5 py-1 text-sm font-bold text-white">
                -{product.discount_percent}% {t("off")}
              </span>
            )}
          </div>
        </div>

        {/* Ma'lumot */}
        <div>
          <h1 className="text-2xl font-extrabold sm:text-3xl">{product.name}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <RatingStars value={parseFloat(product.rating)} />
              {parseFloat(product.rating).toFixed(1)}
            </span>
            <span>· {product.reviews_count} {t("reviews")}</span>
            <span>· {t("sold", { count: product.sold_count })}</span>
            {product.brand && <span>· {t("brand")}: {product.brand.name}</span>}
          </div>

          <div className="mt-5 rounded-2xl bg-gray-50 p-5 dark:bg-gray-900">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-extrabold text-primary">
                {formatSom(product.final_price)} {tc("som")}
              </span>
              {product.discount_price && (
                <span className="text-lg text-gray-400 line-through">
                  {formatSom(product.price)}
                </span>
              )}
            </div>

            <div className="mt-2 text-sm">
              {product.in_stock ? (
                product.stock <= 3 ? (
                  <span className="font-semibold text-warning">{t("onlyLeft", { count: product.stock })}</span>
                ) : (
                  <span className="font-semibold text-success">{t("inStock")}</span>
                )
              ) : (
                <span className="font-semibold text-danger">{t("outOfStock")}</span>
              )}
            </div>

            <div className="mt-4 flex items-center gap-3">
              <div className="flex items-center rounded-xl border border-gray-200 dark:border-gray-700">
                <button onClick={() => setQty((q) => Math.max(1, q - 1))} className="grid h-11 w-11 place-items-center">
                  <Minus className="h-4 w-4" />
                </button>
                <span className="w-8 text-center font-semibold">{qty}</span>
                <button onClick={() => setQty((q) => Math.min(product.stock, q + 1))} className="grid h-11 w-11 place-items-center">
                  <Plus className="h-4 w-4" />
                </button>
              </div>
              <Button onClick={onAdd} disabled={!product.in_stock} loading={add.isPending} size="lg" className="flex-1">
                {!add.isPending && <ShoppingCart className="h-5 w-5" />} {t("addToCart")}
              </Button>
              <WishlistButton productId={product.id} product={product} variant="full" />
            </div>

            <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
              <Truck className="h-4 w-4 text-primary" /> 1–3 kun ichida yetkazib berish · {t("sku")}: {product.sku}
            </div>
          </div>
        </div>
      </div>

      {/* Tablar */}
      <div className="mt-10">
        <div className="flex gap-6 border-b border-gray-100 dark:border-gray-800">
          {(["desc", "reviews"] as const).map((tabKey) => (
            <button
              key={tabKey}
              onClick={() => setTab(tabKey)}
              className={`relative pb-3 text-sm font-semibold transition ${
                tab === tabKey ? "text-primary" : "text-gray-500"
              }`}
            >
              {tabKey === "desc" ? t("description") : `${t("reviews")} (${product.reviews_count})`}
              {tab === tabKey && <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-primary" />}
            </button>
          ))}
        </div>

        <div className="py-6">
          {tab === "desc" ? (
            <p className="max-w-3xl leading-relaxed text-gray-700 dark:text-gray-300">{product.description}</p>
          ) : (
            <div className="space-y-4">
              <ReviewForm slug={slug} />
              {!reviews || reviews.length === 0 ? (
                <p className="text-gray-500">{t("noReviews")}</p>
              ) : (
                reviews.map((r) => (
                  <div key={r.id} className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{r.user_name}</span>
                      <RatingStars value={r.rating} />
                    </div>
                    {r.is_verified && (
                      <span className="mt-1 inline-block rounded bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
                        ✓ Tasdiqlangan xarid
                      </span>
                    )}
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{r.text}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* O'xshash */}
      {product.similar.length > 0 && (
        <div className="mt-6">
          <h2 className="mb-4 text-xl font-extrabold">{t("similar")}</h2>
          <ProductGrid products={product.similar} />
        </div>
      )}
    </div>
  );
}
