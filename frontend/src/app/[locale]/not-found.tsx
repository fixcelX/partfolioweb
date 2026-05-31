"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  const tc = useTranslations("common");
  return (
    <div className="container-zm flex flex-col items-center justify-center py-32 text-center">
      <p className="text-8xl font-black text-primary">404</p>
      <h1 className="mt-4 text-2xl font-extrabold">{tc("notFound")}</h1>
      <Link href="/"><Button size="lg" className="mt-6">{tc("backHome")}</Button></Link>
    </div>
  );
}
