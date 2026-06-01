"use client";

import { motion } from "framer-motion";
import { ArrowRight, Truck, ShieldCheck, Tag } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.05 },
  },
};
const item = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } },
};

export function Hero() {
  const t = useTranslations("home");
  return (
    <section className="container-zm pt-5">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary to-warning bg-[length:200%_200%] px-6 py-12 text-white shadow-hover animate-gradient-shift sm:px-12 sm:py-16">
        {/* Suzuvchi dekorativ doiralar */}
        <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 animate-float-slow rounded-full bg-white/15" />
        <div className="pointer-events-none absolute -bottom-24 right-28 h-52 w-52 animate-float rounded-full bg-white/10" />
        <div className="pointer-events-none absolute left-1/3 top-6 h-24 w-24 animate-float rounded-full bg-white/10" />

        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="relative max-w-xl"
        >
          <motion.span
            variants={item}
            className="inline-flex items-center gap-1 rounded-full bg-white/20 px-3 py-1 text-xs font-semibold backdrop-blur"
          >
            <Tag className="h-3.5 w-3.5" /> {t("promoText")}
          </motion.span>
          <motion.h1
            variants={item}
            className="mt-4 text-3xl font-extrabold leading-tight drop-shadow-sm sm:text-5xl"
          >
            {t("heroTitle")}
          </motion.h1>
          <motion.p
            variants={item}
            className="mt-3 text-base text-white/90 sm:text-lg"
          >
            {t("heroSubtitle")}
          </motion.p>
          <motion.div variants={item}>
            <Link href="/catalog">
              <Button
                size="lg"
                className="mt-6 bg-white text-primary shadow-lg hover:scale-105 hover:bg-white/95"
              >
                {t("heroCta")} <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>

      <motion.div
        variants={container}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-50px" }}
        className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3"
      >
        {[
          { icon: Truck, title: t("featDeliveryT"), text: t("featDeliveryD") },
          { icon: ShieldCheck, title: t("featWarrantyT"), text: t("featWarrantyD") },
          { icon: Tag, title: t("featPriceT"), text: t("featPriceD") },
        ].map((f, i) => (
          <motion.div
            key={i}
            variants={item}
            className="card-hover flex items-center gap-3 rounded-2xl border border-primary-100 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
          >
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary dark:bg-primary-900/30">
              <f.icon className="h-5 w-5" />
            </span>
            <div>
              <p className="font-semibold">{f.title}</p>
              <p className="text-sm text-gray-500">{f.text}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
