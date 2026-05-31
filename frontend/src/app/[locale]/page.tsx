import { setRequestLocale, getTranslations } from "next-intl/server";
import { Hero } from "@/components/home/hero";
import { CategoryStrip } from "@/components/home/category-strip";
import { ProductFeed } from "@/components/home/product-feed";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("home");

  return (
    <div className="pb-8">
      <Hero />
      <CategoryStrip />
      <ProductFeed kind="featured" title={t("featured")} accent="#7000ff" />
      <ProductFeed kind="bestsellers" title={t("bestsellers")} accent="#f59e0b" />
      <ProductFeed kind="new" title={t("new")} accent="#16a34a" />
    </div>
  );
}
