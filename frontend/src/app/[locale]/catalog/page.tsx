import { getTranslations, setRequestLocale } from "next-intl/server";
import { CatalogView } from "@/components/catalog/catalog-view";

export default async function CatalogPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("catalog");
  return <CatalogView title={t("title")} />;
}
