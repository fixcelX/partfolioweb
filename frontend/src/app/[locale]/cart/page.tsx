"use client";

import Image from "next/image";
import { Minus, Plus, ShoppingBag, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useCart, useRemoveCartItem, useUpdateCartItem } from "@/lib/hooks";
import { formatSom } from "@/lib/utils";

export default function CartPage() {
  const t = useTranslations("cart");
  const tc = useTranslations("common");
  const { data: cart, isLoading } = useCart();
  const update = useUpdateCartItem();
  const remove = useRemoveCartItem();

  if (isLoading) {
    return (
      <div className="container-zm py-8">
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container-zm flex flex-col items-center justify-center gap-4 py-24 text-center">
        <ShoppingBag className="h-20 w-20 text-gray-200" />
        <h1 className="text-2xl font-bold">{t("empty")}</h1>
        <p className="text-gray-500">{t("emptyText")}</p>
        <Link href="/catalog"><Button size="lg">{t("goShopping")}</Button></Link>
      </div>
    );
  }

  return (
    <div className="container-zm py-8">
      <h1 className="mb-6 text-2xl font-extrabold">{t("title")}</h1>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {cart.items.map((item) => (
            <div key={item.id} className="flex gap-4 rounded-2xl border border-gray-100 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
              <Link href={`/product/${item.product.slug}`} className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-gray-50 dark:bg-gray-800">
                {item.product.image && <Image src={item.product.image} alt={item.product.name} fill className="object-cover" sizes="96px" />}
              </Link>
              <div className="flex flex-1 flex-col">
                <Link href={`/product/${item.product.slug}`} className="line-clamp-2 font-medium hover:text-primary">
                  {item.product.name}
                </Link>
                <p className="mt-1 text-lg font-bold text-primary">{formatSom(item.subtotal)} {tc("som")}</p>
                <div className="mt-auto flex items-center justify-between">
                  <div className="flex items-center rounded-xl border border-gray-200 dark:border-gray-700">
                    <button onClick={() => item.quantity > 1 && update.mutate({ id: item.id, quantity: item.quantity - 1 })} className="grid h-10 w-10 place-items-center"><Minus className="h-4 w-4" /></button>
                    <span className="w-8 text-center font-semibold">{item.quantity}</span>
                    <button onClick={() => update.mutate({ id: item.id, quantity: item.quantity + 1 })} className="grid h-10 w-10 place-items-center"><Plus className="h-4 w-4" /></button>
                  </div>
                  <button onClick={() => remove.mutate(item.id)} className="flex items-center gap-1 text-sm text-gray-400 hover:text-danger">
                    <Trash2 className="h-4 w-4" /> {t("remove")}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <div className="sticky top-20 rounded-2xl border border-gray-100 p-6 dark:border-gray-800">
            <h3 className="text-lg font-bold">{t("total")}</h3>
            <div className="mt-4 flex justify-between text-sm text-gray-500">
              <span>{t("items")} ({cart.total_quantity})</span>
              <span>{formatSom(cart.total)} {tc("som")}</span>
            </div>
            <div className="mt-3 flex justify-between border-t border-gray-100 pt-3 text-xl font-extrabold dark:border-gray-800">
              <span>{t("total")}</span>
              <span className="text-primary">{formatSom(cart.total)} {tc("som")}</span>
            </div>
            <Link href="/checkout"><Button size="lg" className="mt-5 w-full">{t("checkout")}</Button></Link>
          </div>
        </div>
      </div>
    </div>
  );
}
