"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";

function SuccessInner() {
  const t = useTranslations("success");
  const params = useSearchParams();
  const number = params.get("number") ?? params.get("order") ?? "—";

  return (
    <div className="container-zm flex flex-col items-center justify-center py-24 text-center">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200, damping: 14 }}
      >
        <CheckCircle2 className="h-24 w-24 text-success" />
      </motion.div>
      <h1 className="mt-6 text-3xl font-extrabold">{t("title")}</h1>
      <p className="mt-3 max-w-md text-gray-500">{t("text", { number })}</p>
      <div className="mt-8 flex gap-3">
        <Link href="/account"><Button size="lg">{t("toOrders")}</Button></Link>
        <Link href="/"><Button size="lg" variant="outline">{t("toHome")}</Button></Link>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense>
      <SuccessInner />
    </Suspense>
  );
}
