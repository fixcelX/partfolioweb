"use client";

import Image from "next/image";
import { AnimatePresence, motion } from "framer-motion";
import { Minus, Plus, ShoppingBag, Trash2, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { useCart, useRemoveCartItem, useUpdateCartItem } from "@/lib/hooks";
import { useUI } from "@/stores/ui";
import { formatSom } from "@/lib/utils";

export function CartDrawer() {
  const t = useTranslations("cart");
  const tc = useTranslations("common");
  const { cartOpen, closeCart } = useUI();
  const { data: cart } = useCart();
  const update = useUpdateCartItem();
  const remove = useRemoveCartItem();
  const router = useRouter();

  const items = cart?.items ?? [];

  const goCheckout = () => {
    closeCart();
    router.push("/checkout");
  };

  return (
    <AnimatePresence>
      {cartOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeCart}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "tween", duration: 0.25 }}
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-gray-950"
          >
            <header className="flex items-center justify-between border-b border-gray-100 px-5 py-4 dark:border-gray-800">
              <h2 className="flex items-center gap-2 text-lg font-extrabold">
                <ShoppingBag className="h-5 w-5 text-primary" /> {t("title")}
                {cart && cart.total_quantity > 0 && (
                  <span className="rounded-full bg-primary px-2 py-0.5 text-xs text-white">
                    {cart.total_quantity}
                  </span>
                )}
              </h2>
              <button
                onClick={closeCart}
                aria-label="close"
                className="grid h-9 w-9 place-items-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <X className="h-5 w-5" />
              </button>
            </header>

            {items.length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
                <ShoppingBag className="h-16 w-16 text-gray-200" />
                <p className="text-gray-500">{t("emptyText")}</p>
                <Button onClick={closeCart}>{t("goShopping")}</Button>
              </div>
            ) : (
              <>
                <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      className="flex gap-3 rounded-2xl border border-gray-100 p-3 dark:border-gray-800"
                    >
                      <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-gray-50 dark:bg-gray-800">
                        {item.product.image && (
                          <Image
                            src={item.product.image}
                            alt={item.product.name}
                            fill
                            sizes="80px"
                            className="object-cover"
                          />
                        )}
                      </div>
                      <div className="flex flex-1 flex-col">
                        <Link
                          href={`/product/${item.product.slug}`}
                          onClick={closeCart}
                          className="line-clamp-2 text-sm font-medium hover:text-primary"
                        >
                          {item.product.name}
                        </Link>
                        <p className="mt-1 font-bold text-primary">
                          {formatSom(item.subtotal)} {tc("som")}
                        </p>
                        <div className="mt-auto flex items-center justify-between">
                          <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-700">
                            <button
                              onClick={() =>
                                item.quantity > 1 &&
                                update.mutate({
                                  id: item.id,
                                  quantity: item.quantity - 1,
                                })
                              }
                              className="grid h-8 w-8 place-items-center disabled:opacity-40"
                              disabled={item.quantity <= 1}
                            >
                              <Minus className="h-3.5 w-3.5" />
                            </button>
                            <span className="w-7 text-center text-sm font-semibold">
                              {item.quantity}
                            </span>
                            <button
                              onClick={() =>
                                update.mutate({
                                  id: item.id,
                                  quantity: item.quantity + 1,
                                })
                              }
                              className="grid h-8 w-8 place-items-center"
                            >
                              <Plus className="h-3.5 w-3.5" />
                            </button>
                          </div>
                          <button
                            onClick={() => remove.mutate(item.id)}
                            aria-label={t("remove")}
                            className="text-gray-400 hover:text-danger"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <footer className="border-t border-gray-100 px-5 py-4 dark:border-gray-800">
                  <div className="mb-3 flex items-center justify-between text-lg font-extrabold">
                    <span>{t("total")}</span>
                    <span className="text-primary">
                      {formatSom(cart?.total ?? 0)} {tc("som")}
                    </span>
                  </div>
                  <Button size="lg" className="w-full" onClick={goCheckout}>
                    {t("checkout")}
                  </Button>
                  <Link
                    href="/cart"
                    onClick={closeCart}
                    className="mt-2 block text-center text-sm text-gray-500 hover:text-primary"
                  >
                    {tc("viewCart")}
                  </Link>
                </footer>
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
