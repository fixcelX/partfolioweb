import { setRequestLocale } from "next-intl/server";
import { CatalogView } from "@/components/catalog/catalog-view";

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const title = slug
    .split("-")
    .map((s) => s[0]?.toUpperCase() + s.slice(1))
    .join(" ");
  return <CatalogView categorySlug={slug} title={title} />;
}
