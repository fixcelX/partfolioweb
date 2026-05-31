"use client";

import { XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";

export default function FailedPage() {
  const tc = useTranslations("common");
  return (
    <div className="container-zm flex flex-col items-center justify-center py-24 text-center">
      <XCircle className="h-24 w-24 text-danger" />
      <h1 className="mt-6 text-3xl font-extrabold">{tc("error")}</h1>
      <p className="mt-3 text-gray-500">To'lov amalga oshmadi. Iltimos qayta urinib ko'ring.</p>
      <div className="mt-8 flex gap-3">
        <Link href="/checkout"><Button size="lg">{tc("retry")}</Button></Link>
        <Link href="/"><Button size="lg" variant="outline">{tc("backHome")}</Button></Link>
      </div>
    </div>
  );
}
