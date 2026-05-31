"use client";

import { motion } from "framer-motion";
import { ArrowRight, Truck, ShieldCheck, Tag } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";

export function Hero() {
  const t = useTranslations("home");
  return (
    <section className="container-zm pt-5">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary to-primary-400 px-6 py-12 text-white sm:px-12 sm:py-16">
        <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/10" />
        <div className="absolute -bottom-20 right-24 h-48 w-48 rounded-full bg-white/10" />
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative max-w-xl"
        >
          <span className="inline-flex items-center gap-1 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold">
            <Tag className="h-3.5 w-3.5" /> {t("promoText")}
          </span>
          <h1 className="mt-4 text-3xl font-extrabold leading-tight sm:text-5xl">
            {t("heroTitle")}
          </h1>
          <p className="mt-3 text-base text-white/80 sm:text-lg">
            {t("heroSubtitle")}
          </p>
          <Link href="/catalog">
            <Button size="lg" variant="outline" className="mt-6 border-white bg-white text-primary hover:bg-white/90">
              {t("heroCta")} <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          { icon: Truck, title: t("featDeliveryT"), text: t("featDeliveryD") },
          { icon: ShieldCheck, title: t("featWarrantyT"), text: t("featWarrantyD") },
          { icon: Tag, title: t("featPriceT"), text: t("featPriceD") },
        ].map((f, i) => (
          <div key={i} className="flex items-center gap-3 rounded-2xl border border-gray-100 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-primary-50 text-primary dark:bg-primary-900/30">
              <f.icon className="h-5 w-5" />
            </span>
            <div>
              <p className="font-semibold">{f.title}</p>
              <p className="text-sm text-gray-500">{f.text}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
