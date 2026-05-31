import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export function Footer() {
  const t = useTranslations("footer");
  const tn = useTranslations("nav");
  return (
    <footer className="mt-16 border-t border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-gray-950">
      <div className="container-zm grid gap-8 py-12 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary font-black text-white">Z</span>
            <span className="text-lg font-extrabold">ZAMON<span className="text-primary">MARKET</span></span>
          </div>
          <p className="mt-3 max-w-xs text-sm text-gray-500">{t("about")}</p>
        </div>
        <div>
          <h4 className="font-bold">{t("company")}</h4>
          <ul className="mt-3 space-y-2 text-sm text-gray-500">
            <li><Link href="/catalog" className="hover:text-primary">{tn("catalog")}</Link></li>
            <li><Link href="/account" className="hover:text-primary">{tn("account")}</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold">{t("help")}</h4>
          <ul className="mt-3 space-y-2 text-sm text-gray-500">
            <li><a href="/api/docs/" className="hover:text-primary">API hujjat</a></li>
            <li><Link href="/cart" className="hover:text-primary">{tn("cart")}</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold">Click · Payme · Stripe</h4>
          <p className="mt-3 text-sm text-gray-500">Xavfsiz to'lov tizimlari bilan.</p>
        </div>
      </div>
      <div className="border-t border-gray-100 py-5 text-center text-xs text-gray-400 dark:border-gray-800">
        © {new Date().getFullYear()} ZAMON MARKET. {t("rights")}.
      </div>
    </footer>
  );
}
