"use client";

import { useEffect, useState } from "react";
import {
  LogOut,
  MapPin,
  Package,
  Plus,
  Star,
  Trash2,
  User as UserIcon,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import {
  useAddresses,
  useCreateAddress,
  useDeleteAddress,
  useOrders,
  useSetDefaultAddress,
  useUpdateProfile,
} from "@/lib/hooks";
import { useAuth } from "@/stores/auth";
import { formatSom } from "@/lib/utils";
import type { Address, OrderStatus } from "@/lib/types";

const STEPS: OrderStatus[] = ["pending", "paid", "shipped", "delivered"];
type Tab = "profile" | "orders" | "addresses";

export default function AccountPage() {
  const t = useTranslations("account");
  const ts = useTranslations("status");
  const tc = useTranslations("common");
  const tn = useTranslations("nav");
  const tCart = useTranslations("cart");
  const router = useRouter();
  const { user, logout, hydrated } = useAuth();
  const [tab, setTab] = useState<Tab>("profile");

  useEffect(() => {
    if (hydrated && !user) router.replace("/login?next=/account");
  }, [hydrated, user, router]);

  if (!user) return null;

  const tabs: { id: Tab; label: string; icon: typeof UserIcon }[] = [
    { id: "profile", label: t("tabProfile"), icon: UserIcon },
    { id: "orders", label: t("orders"), icon: Package },
    { id: "addresses", label: t("tabAddresses"), icon: MapPin },
  ];

  return (
    <div className="container-zm py-8">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary text-white">
            <UserIcon className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-xl font-extrabold">
              {user.first_name || t("title")}
            </h1>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => {
            logout();
            router.push("/");
          }}
        >
          <LogOut className="h-4 w-4" /> {tn("logout")}
        </Button>
      </div>

      {/* Tablar */}
      <div className="mb-6 flex gap-2 overflow-x-auto border-b border-gray-100 dark:border-gray-800">
        {tabs.map((tb) => (
          <button
            key={tb.id}
            onClick={() => setTab(tb.id)}
            className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-sm font-semibold transition ${
              tab === tb.id
                ? "border-primary text-primary"
                : "border-transparent text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
            }`}
          >
            <tb.icon className="h-4 w-4" /> {tb.label}
          </button>
        ))}
      </div>

      {tab === "profile" && <ProfileTab />}
      {tab === "orders" && (
        <OrdersTab t={t} ts={ts} tc={tc} tCart={tCart} />
      )}
      {tab === "addresses" && <AddressesTab />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Profil tab
// ---------------------------------------------------------------------------
function ProfileTab() {
  const t = useTranslations("account");
  const tc = useTranslations("common");
  const toast = useToast();
  const user = useAuth((s) => s.user);
  const update = useUpdateProfile();
  const [form, setForm] = useState({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    phone: user?.phone ?? "",
  });

  const onSave = (e: React.FormEvent) => {
    e.preventDefault();
    update.mutate(form, {
      onSuccess: () => toast.push(t("saved")),
      onError: () => toast.push(tc("error"), "error"),
    });
  };

  return (
    <form
      onSubmit={onSave}
      className="max-w-lg space-y-4 rounded-2xl border border-gray-100 p-6 dark:border-gray-800"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label={t("firstName")}
          value={form.first_name}
          onChange={(e) => setForm({ ...form, first_name: e.target.value })}
        />
        <Input
          label={t("lastName")}
          value={form.last_name}
          onChange={(e) => setForm({ ...form, last_name: e.target.value })}
        />
      </div>
      <Input
        label={t("phone")}
        value={form.phone}
        onChange={(e) => setForm({ ...form, phone: e.target.value })}
        placeholder="+998 90 123 45 67"
      />
      <Input label={t("email")} value={user?.email ?? ""} disabled />
      <Button type="submit" loading={update.isPending}>
        {t("save")}
      </Button>
    </form>
  );
}

// ---------------------------------------------------------------------------
// Buyurtmalar tab
// ---------------------------------------------------------------------------
function OrdersTab({
  t,
  ts,
  tc,
  tCart,
}: {
  t: ReturnType<typeof useTranslations>;
  ts: ReturnType<typeof useTranslations>;
  tc: ReturnType<typeof useTranslations>;
  tCart: ReturnType<typeof useTranslations>;
}) {
  const { data: orders, isLoading } = useOrders();

  if (isLoading) return <Skeleton className="h-32 w-full rounded-2xl" />;
  if (!orders || orders.length === 0)
    return (
      <div className="grid place-items-center rounded-2xl border border-dashed border-gray-200 py-16 text-gray-500 dark:border-gray-700">
        {t("noOrders")}
      </div>
    );

  return (
    <div className="space-y-4">
      {orders.map((order) => {
        const stepIndex = STEPS.indexOf(order.status);
        const cancelled = order.status === "cancelled";
        return (
          <div
            key={order.id}
            className="rounded-2xl border border-gray-100 p-5 dark:border-gray-800"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <span className="font-bold">
                  {t("orderNumber")} {order.number}
                </span>
                <span className="ml-3 text-sm text-gray-400">
                  {new Date(order.created_at).toLocaleDateString()}
                </span>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  cancelled
                    ? "bg-danger/10 text-danger"
                    : "bg-primary-50 text-primary dark:bg-primary-900/20"
                }`}
              >
                {ts(order.status)}
              </span>
            </div>

            {!cancelled && (
              <div className="mt-5 flex items-center">
                {STEPS.map((step, i) => (
                  <div
                    key={step}
                    className="flex flex-1 items-center last:flex-none"
                  >
                    <div className="flex flex-col items-center">
                      <span
                        className={`grid h-7 w-7 place-items-center rounded-full text-xs font-bold ${
                          i <= stepIndex
                            ? "bg-primary text-white"
                            : "bg-gray-200 text-gray-400 dark:bg-gray-700"
                        }`}
                      >
                        {i + 1}
                      </span>
                      <span className="mt-1 text-[11px] text-gray-500">
                        {ts(step)}
                      </span>
                    </div>
                    {i < STEPS.length - 1 && (
                      <span
                        className={`mx-1 h-0.5 flex-1 ${
                          i < stepIndex
                            ? "bg-primary"
                            : "bg-gray-200 dark:bg-gray-700"
                        }`}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="mt-4 space-y-1 border-t border-gray-50 pt-3 text-sm dark:border-gray-900">
              {order.items.map((it) => (
                <div key={it.id} className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    {it.product_name} × {it.quantity}
                  </span>
                  <span>
                    {formatSom(it.subtotal)} {tc("som")}
                  </span>
                </div>
              ))}
              <div className="flex justify-between border-t border-gray-50 pt-2 font-bold dark:border-gray-900">
                <span>{tCart("total")}</span>
                <span className="text-primary">
                  {formatSom(order.total)} {tc("som")}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Manzillar tab
// ---------------------------------------------------------------------------
const emptyAddr: Omit<Address, "id"> = {
  full_name: "",
  phone: "",
  region: "",
  city: "",
  street: "",
  zip_code: "",
  is_default: false,
};

function AddressesTab() {
  const t = useTranslations("account");
  const tc = useTranslations("common");
  const toast = useToast();
  const { data: addresses, isLoading } = useAddresses();
  const create = useCreateAddress();
  const del = useDeleteAddress();
  const setDefault = useSetDefaultAddress();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<Omit<Address, "id">>(emptyAddr);

  const onCreate = (e: React.FormEvent) => {
    e.preventDefault();
    create.mutate(form, {
      onSuccess: () => {
        toast.push(t("saved"));
        setForm(emptyAddr);
        setOpen(false);
      },
      onError: () => toast.push(tc("error"), "error"),
    });
  };

  return (
    <div className="space-y-4">
      {isLoading ? (
        <Skeleton className="h-24 w-full rounded-2xl" />
      ) : !addresses || addresses.length === 0 ? (
        <div className="grid place-items-center rounded-2xl border border-dashed border-gray-200 py-12 text-gray-500 dark:border-gray-700">
          {t("noAddresses")}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {addresses.map((a) => (
            <div
              key={a.id}
              className="rounded-2xl border border-gray-100 p-5 dark:border-gray-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2 font-bold">
                  <MapPin className="h-4 w-4 text-primary" /> {a.full_name}
                  {a.is_default && (
                    <span className="rounded-full bg-primary-50 px-2 py-0.5 text-[11px] font-semibold text-primary dark:bg-primary-900/20">
                      {t("default")}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => del.mutate(a.id)}
                  aria-label={tc("error")}
                  className="text-gray-400 hover:text-danger"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {a.region}, {a.city}, {a.street}
              </p>
              <p className="text-sm text-gray-500">{a.phone}</p>
              {!a.is_default && (
                <button
                  onClick={() => setDefault.mutate(a.id)}
                  className="mt-3 inline-flex items-center gap-1 text-sm font-semibold text-primary hover:underline"
                >
                  <Star className="h-3.5 w-3.5" /> {t("setDefault")}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {open ? (
        <form
          onSubmit={onCreate}
          className="space-y-4 rounded-2xl border border-gray-100 p-6 dark:border-gray-800"
        >
          <h3 className="font-bold">{t("newAddress")}</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label={t("fullName")}
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
            <Input
              label={t("phone")}
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              required
            />
            <Input
              label={t("region")}
              value={form.region}
              onChange={(e) => setForm({ ...form, region: e.target.value })}
              required
            />
            <Input
              label={t("city")}
              value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
              required
            />
          </div>
          <Input
            label={t("street")}
            value={form.street}
            onChange={(e) => setForm({ ...form, street: e.target.value })}
            required
          />
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.is_default}
              onChange={(e) =>
                setForm({ ...form, is_default: e.target.checked })
              }
            />
            {t("setDefault")}
          </label>
          <div className="flex gap-3">
            <Button type="submit" loading={create.isPending}>
              {t("save")}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => setOpen(false)}
            >
              {tc("cancel")}
            </Button>
          </div>
        </form>
      ) : (
        <Button variant="outline" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> {t("addAddress")}
        </Button>
      )}
    </div>
  );
}
