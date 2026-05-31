import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { ProductDetailView } from "@/components/product/product-detail";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string; locale: string }>;
}): Promise<Metadata> {
  const { slug, locale } = await params;
  try {
    const res = await fetch(`${API}/products/${slug}/?lang=${locale}`, {
      next: { revalidate: 120 },
    });
    if (!res.ok) return { title: "Mahsulot" };
    const p = await res.json();
    return {
      title: p.name,
      description: p.description?.slice(0, 160),
      openGraph: { title: p.name, images: p.image ? [p.image] : [] },
    };
  } catch {
    return { title: "Mahsulot" };
  }
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  return <ProductDetailView slug={slug} />;
}
