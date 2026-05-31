"use client";

import { useState } from "react";
import { Globe, ChevronDown } from "lucide-react";
import { useLocale } from "next-intl";
import { usePathname, useRouter } from "@/i18n/routing";

const LOCALES = [
  { code: "uz", label: "O'zbekcha" },
  { code: "ru", label: "Русский" },
  { code: "en", label: "English" },
] as const;

export function LangSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const change = (code: string) => {
    setOpen(false);
    document.cookie = `NEXT_LOCALE=${code};path=/;max-age=31536000`;
    router.replace(pathname, { locale: code });
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 rounded-lg px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
      >
        <Globe className="h-4 w-4" />
        <span className="hidden uppercase sm:inline">{locale}</span>
        <ChevronDown className="h-3 w-3" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-20 mt-1 w-36 overflow-hidden rounded-xl border border-gray-100 bg-white py-1 shadow-hover dark:border-gray-800 dark:bg-gray-900">
            {LOCALES.map((l) => (
              <button
                key={l.code}
                onClick={() => change(l.code)}
                className={`block w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800 ${
                  l.code === locale ? "font-bold text-primary" : "text-gray-700 dark:text-gray-200"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
