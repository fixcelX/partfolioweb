"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CreditCard } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useCart, useCheckout } from "@/lib/hooks";
import { api } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { formatSom } from "@/lib/utils";

const schema = z.object({
  full_name: z.string().min(2),
  phone: z.string().min(7),
  region: z.string().min(2),
  city: z.string().min(2),
  street: z.string().min(2),
  payment_method: z.enum(["click", "payme", "stripe", "cod"]),
});
type FormData = z.infer<typeof schema>;

const PAYMENTS = [
  { id: "click", label: "Click" },
  { id: "payme", label: "Payme" },
  { id: "stripe", label: "Stripe" },
  { id: "cod", label: "cod" },
] as const;

export default function CheckoutPage() {
  const t = useTranslations("checkout");
  const tc = useTranslations("common");
  const tCart = useTranslations("cart");
  const router = useRouter();
  const toast = useToast();
  const { data: cart } = useCart();
  const checkout = useCheckout();
  const user = useAuth((s) => s.user);
  const hydrated = useAuth((s) => s.hydrated);

  const { register, handleSubmit, watch, setValue, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { payment_method: "click", full_name: user?.first_name ?? "" },
  });
  const method = watch("payment_method");

  useEffect(() => {
    if (hydrated && !user) router.replace("/login?next=/checkout");
  }, [hydrated, user, router]);

  const onSubmit = async (data: FormData) => {
    try {
      const order = await checkout.mutateAsync(data);
      if (data.payment_method !== "cod") {
        const res = await api.post(`/payments/${data.payment_method}/create/`, {
          order: order.number,
        });
        // Real provayderda res.data.payment_url ga redirect bo'ladi.
        // Demo: success sahifasiga o'tamiz.
        void res;
      }
      router.push(`/checkout/success?number=${order.number}`);
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        tc("error");
      toast.push(msg, "error");
    }
  };

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container-zm py-24 text-center">
        <p className="text-gray-500">{tCart("empty")}</p>
        <Link href="/catalog"><Button className="mt-4">{tc("backHome")}</Button></Link>
      </div>
    );
  }

  return (
    <div className="container-zm py-8">
      <h1 className="mb-6 text-2xl font-extrabold">{t("title")}</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="rounded-2xl border border-gray-100 p-6 dark:border-gray-800">
            <h2 className="mb-4 text-lg font-bold">{t("delivery")}</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label={t("fullName")} error={!!formState.errors.full_name} {...register("full_name")} />
              <Field label={t("phone")} error={!!formState.errors.phone} {...register("phone")} placeholder="+998 90 123 45 67" />
              <Field label={t("region")} error={!!formState.errors.region} {...register("region")} />
              <Field label={t("city")} error={!!formState.errors.city} {...register("city")} />
              <div className="sm:col-span-2">
                <Field label={t("street")} error={!!formState.errors.street} {...register("street")} />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-gray-100 p-6 dark:border-gray-800">
            <h2 className="mb-4 text-lg font-bold">{t("payment")}</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {PAYMENTS.map((p) => (
                <button
                  type="button"
                  key={p.id}
                  onClick={() => setValue("payment_method", p.id)}
                  className={`flex h-16 items-center justify-center gap-2 rounded-xl border-2 font-semibold transition ${
                    method === p.id
                      ? "border-primary bg-primary-50 text-primary dark:bg-primary-900/20"
                      : "border-gray-200 dark:border-gray-700"
                  }`}
                >
                  <CreditCard className="h-4 w-4" />
                  {p.id === "cod" ? t("cod") : p.label}
                </button>
              ))}
            </div>
          </section>
        </div>

        <div className="lg:col-span-1">
          <div className="sticky top-20 rounded-2xl border border-gray-100 p-6 dark:border-gray-800">
            <h3 className="text-lg font-bold">{t("summary")}</h3>
            <div className="mt-4 max-h-48 space-y-2 overflow-y-auto text-sm">
              {cart.items.map((i) => (
                <div key={i.id} className="flex justify-between gap-2">
                  <span className="line-clamp-1 text-gray-600 dark:text-gray-400">{i.product.name} × {i.quantity}</span>
                  <span className="shrink-0 font-medium">{formatSom(i.subtotal)}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-between border-t border-gray-100 pt-4 text-xl font-extrabold dark:border-gray-800">
              <span>{tCart("total")}</span>
              <span className="text-primary">{formatSom(cart.total)} {tc("som")}</span>
            </div>
            <Button type="submit" size="lg" className="mt-5 w-full" disabled={checkout.isPending}>
              {checkout.isPending ? t("processing") : t("placeOrder")}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}

const Field = ({
  label,
  error,
  ...props
}: { label: string; error?: boolean } & React.InputHTMLAttributes<HTMLInputElement>) => (
  <label className="block">
    <span className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
    <input
      {...props}
      className={`h-11 w-full rounded-xl border px-3 text-sm outline-none focus:ring-2 focus:ring-primary/20 dark:bg-gray-800 ${
        error ? "border-danger" : "border-gray-200 focus:border-primary dark:border-gray-700"
      }`}
    />
  </label>
);
