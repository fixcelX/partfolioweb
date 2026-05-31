"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { CatalogView } from "@/components/catalog/catalog-view";

function SearchInner() {
  const params = useSearchParams();
  const q = params.get("q") ?? "";
  const t = useTranslations("nav");
  return <CatalogView search={q} title={`${t("search")}: "${q}"`} />;
}

export default function SearchPage() {
  return (
    <Suspense>
      <SearchInner />
    </Suspense>
  );
}
