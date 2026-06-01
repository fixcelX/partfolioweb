"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ShoppingCart } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { RatingStars } from "@/components/ui/rating-stars";
import { WishlistButton } from "./wishlist-button";
import { useToast } from "@/components/ui/toast";
import { useAddToCart } from "@/lib/hooks";
import { cn, formatSom } from "@/lib/utils";
import type { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  const t = useTranslations("product");
  const tc = useTranslations("common");
  const add = useAddToCart();
  const toast = useToast();

  const onAdd = (e: React.MouseEvent) => {
    e.preventDefault();
    add.mutate(
      { product_id: product.id, quantity: 1, product },
      {
        onSuccess: () => toast.push(t("added")),
        onError: () => toast.push(tc("error"), "error"),
      },
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      whileHover={{ y: -6 }}
      className="group relative flex h-full flex-col rounded-2xl border border-primary-100/70 bg-white p-3 shadow-card transition-shadow hover:shadow-hover dark:border-gray-800 dark:bg-gray-900"
    >
      <WishlistButton productId={product.id} product={product} />
      <Link href={`/product/${product.slug}`} className="flex flex-1 flex-col">
        <div className="relative aspect-square overflow-hidden rounded-xl bg-gray-50 dark:bg-gray-800">
          {product.image ? (
            <Image
              src={product.image}
              alt={product.name}
              fill
              sizes="(max-width:768px) 50vw, 240px"
              className="object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-300">
              <ShoppingCart className="h-10 w-10" />
            </div>
          )}
          {product.discount_percent > 0 && (
            <span className="absolute left-2 top-2 rounded-lg bg-danger px-2 py-0.5 text-xs font-bold text-white">
              -{product.discount_percent}%
            </span>
          )}
          {product.stock > 0 && product.stock <= 3 && (
            <span className="absolute bottom-2 left-2 rounded-lg bg-warning px-2 py-0.5 text-[11px] font-semibold text-white">
              {t("onlyLeft", { count: product.stock })}
            </span>
          )}
        </div>

        <div className="mt-3 flex flex-1 flex-col">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-extrabold text-gray-900 dark:text-white">
              {formatSom(product.final_price)}
            </span>
            {product.discount_price && (
              <span className="text-sm text-gray-400 line-through">
                {formatSom(product.price)}
              </span>
            )}
          </div>
          <p className="mt-1 line-clamp-2 text-sm text-gray-700 dark:text-gray-300">
            {product.name}
          </p>
          <div className="mt-auto flex items-center gap-1.5 pt-2 text-xs text-gray-500">
            <RatingStars value={parseFloat(product.rating)} />
            <span>{parseFloat(product.rating).toFixed(1)}</span>
            <span className="text-gray-300">·</span>
            <span>{product.reviews_count}</span>
          </div>
        </div>
      </Link>

      <Button
        onClick={onAdd}
        disabled={!product.in_stock}
        loading={add.isPending}
        size="sm"
        className={cn("mt-3 w-full", !product.in_stock && "opacity-60")}
      >
        {!add.isPending && <ShoppingCart className="h-4 w-4" />}
        {product.in_stock ? t("addToCart") : t("outOfStock")}
      </Button>
    </motion.div>
  );
}
