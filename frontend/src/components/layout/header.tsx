"use client";

import { useState } from "react";
import { Heart, LayoutGrid, ShoppingCart, User as UserIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { LangSwitcher } from "./lang-switcher";
import { CategoriesMenu } from "./categories-menu";
import { SearchBar } from "./search-bar";
import { ThemeToggle } from "./theme-toggle";
import { useCart } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";

export function Header() {
  const t = useTranslations("nav");
  const { data: cart } = useCart();
  const user = useAuth((s) => s.user);
  const [menuOpen, setMenuOpen] = useState(false);

  const count = cart?.total_quantity ?? 0;

  return (
    <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/90 backdrop-blur dark:border-gray-800 dark:bg-gray-950/90">
      <div className="container-zm flex h-16 items-center gap-3 sm:gap-5">
        <Link href="/" className="flex shrink-0 items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary font-black text-white">
            Z
          </span>
          <span className="hidden text-lg font-extrabold tracking-tight text-gray-900 dark:text-white sm:block">
            ZAMON<span className="text-primary">MARKET</span>
          </span>
        </Link>

        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="hidden items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-600 md:flex"
        >
          <LayoutGrid className="h-4 w-4" />
          {t("catalog")}
        </button>

        <SearchBar />

        <nav className="flex items-center gap-1">
          <ThemeToggle />
          <LangSwitcher />
          <Link
            prefetch
            href="/account"
            className="flex flex-col items-center rounded-lg px-2 py-1.5 text-gray-700 transition-transform hover:-translate-y-0.5 hover:bg-gray-100 active:scale-95 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            <UserIcon className="h-5 w-5" />
            <span className="hidden text-[11px] lg:block">
              {user ? user.first_name || t("account") : t("login")}
            </span>
          </Link>
          <Link
            prefetch
            href="/wishlist"
            className="hidden flex-col items-center rounded-lg px-2 py-1.5 text-gray-700 transition-transform hover:-translate-y-0.5 hover:bg-gray-100 active:scale-95 sm:flex dark:text-gray-200 dark:hover:bg-gray-800"
          >
            <Heart className="h-5 w-5" />
            <span className="hidden text-[11px] lg:block">{t("wishlist")}</span>
          </Link>
          <Link
            prefetch
            href="/cart"
            aria-label={t("cart")}
            className="relative flex flex-col items-center rounded-lg px-2 py-1.5 text-gray-700 transition-transform hover:-translate-y-0.5 hover:bg-gray-100 active:scale-95 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            <ShoppingCart className="h-5 w-5" />
            <span className="hidden text-[11px] lg:block">{t("cart")}</span>
            {count > 0 && (
              <span className="absolute -right-0.5 top-0 grid h-5 min-w-5 place-items-center rounded-full bg-danger px-1 text-[11px] font-bold text-white">
                {count}
              </span>
            )}
          </Link>
        </nav>
      </div>

      {menuOpen && <CategoriesMenu onClose={() => setMenuOpen(false)} />}
    </header>
  );
}
