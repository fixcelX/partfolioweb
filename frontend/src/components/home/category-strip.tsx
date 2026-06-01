"use client";

import * as Icons from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { useCategories } from "@/lib/hooks";
import { Skeleton } from "@/components/ui/skeleton";

export function CategoryStrip() {
  const t = useTranslations("home");
  const { data: categories, isLoading } = useCategories();

  return (
    <section className="container-zm mt-10">
      <h2 className="mb-4 inline-block text-xl font-extrabold text-gradient sm:text-2xl">{t("categories")}</h2>
      {isLoading ? (
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-8">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-8">
          {categories?.map((cat) => {
            const Icon =
              (Icons[
                (cat.icon
                  .split("-")
                  .map((s) => s[0].toUpperCase() + s.slice(1))
                  .join("")) as keyof typeof Icons
              ] as Icons.LucideIcon) ?? Icons.Package;
            return (
              <Link
                key={cat.id}
                href={`/category/${cat.slug}`}
                className="group flex flex-col items-center gap-2 rounded-2xl border border-primary-100/70 bg-white p-3 text-center transition-all duration-200 hover:-translate-y-1 hover:border-primary hover:shadow-hover dark:border-gray-800 dark:bg-gray-900"
              >
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-primary-50 text-primary transition-transform duration-200 group-hover:-rotate-6 group-hover:scale-110 dark:bg-primary-900/30">
                  <Icon className="h-6 w-6" />
                </span>
                <span className="line-clamp-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                  {cat.name}
                </span>
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
