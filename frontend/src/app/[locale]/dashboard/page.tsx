"use client";

import { useEffect } from "react";
import { BarChart3, Box, Star, TrendingUp } from "lucide-react";
import { useRouter } from "@/i18n/routing";
import { Skeleton } from "@/components/ui/skeleton";
import { useProductFeed, useProducts } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";
import { formatSom } from "@/lib/utils";

export default function DashboardPage() {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const hydrated = useAuth((s) => s.hydrated);
  const { data: all } = useProducts({ page_size: 1 });
  const { data: best, isLoading } = useProductFeed("bestsellers");

  useEffect(() => {
    if (!hydrated) return;
    if (user && user.role !== "admin" && user.role !== "seller") {
      router.replace("/account");
    } else if (!user) {
      router.replace("/login?next=/dashboard");
    }
  }, [hydrated, user, router]);

  if (!user) return null;

  const maxSold = Math.max(...(best?.map((p) => p.sold_count) ?? [1]), 1);
  const revenue = (best ?? []).reduce(
    (sum, p) => sum + p.sold_count * parseFloat(p.final_price),
    0,
  );

  const stats = [
    { icon: Box, label: "Mahsulotlar", value: all?.count ?? "—" },
    { icon: TrendingUp, label: "Taxminiy savdo (top)", value: `${formatSom(revenue)} so'm` },
    { icon: Star, label: "Top mahsulotlar", value: best?.length ?? 0 },
  ];

  return (
    <div className="container-zm py-8">
      <h1 className="mb-6 flex items-center gap-2 text-2xl font-extrabold">
        <BarChart3 className="h-6 w-6 text-primary" /> Dashboard
      </h1>

      <div className="grid gap-4 sm:grid-cols-3">
        {stats.map((s, i) => (
          <div key={i} className="rounded-2xl border border-gray-100 p-5 dark:border-gray-800">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary-50 text-primary dark:bg-primary-900/30">
              <s.icon className="h-5 w-5" />
            </span>
            <p className="mt-3 text-2xl font-extrabold">{s.value}</p>
            <p className="text-sm text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-2xl border border-gray-100 p-6 dark:border-gray-800">
        <h2 className="mb-5 text-lg font-bold">Eng ko'p sotilgan mahsulotlar</h2>
        {isLoading ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <div className="space-y-3">
            {best?.slice(0, 8).map((p) => (
              <div key={p.id} className="flex items-center gap-3">
                <span className="line-clamp-1 w-48 shrink-0 text-sm">{p.name}</span>
                <div className="h-6 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                  <div
                    className="flex h-full items-center justify-end rounded-full bg-primary px-2 text-[11px] font-bold text-white"
                    style={{ width: `${Math.max((p.sold_count / maxSold) * 100, 8)}%` }}
                  >
                    {p.sold_count}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
