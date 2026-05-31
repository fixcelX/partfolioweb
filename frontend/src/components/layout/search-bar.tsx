"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { Search, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/routing";
import { useProducts } from "@/lib/hooks";
import { formatSom } from "@/lib/utils";

export function SearchBar() {
  const t = useTranslations("nav");
  const tc = useTranslations("common");
  const router = useRouter();
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");
  const [open, setOpen] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // debounce 300ms
  useEffect(() => {
    const id = setTimeout(() => setDebounced(q.trim()), 300);
    return () => clearTimeout(id);
  }, [q]);

  const { data, isFetching } = useProducts({
    search: debounced.length >= 2 ? debounced : undefined,
    page_size: 6,
  });

  // tashqariga bosilganda yopish
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) {
      setOpen(false);
      router.push(`/search?q=${encodeURIComponent(q.trim())}`);
    }
  };

  const showDropdown = open && debounced.length >= 2;
  const results = data?.results ?? [];

  return (
    <div ref={boxRef} className="relative flex-1">
      <form onSubmit={submit} className="relative">
        <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder={t("search")}
          className="h-11 w-full rounded-xl border border-gray-200 bg-gray-50 pl-10 pr-9 text-sm outline-none transition focus:border-primary focus:bg-white focus:ring-2 focus:ring-primary/20 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />
        {q && (
          <button
            type="button"
            onClick={() => {
              setQ("");
              setOpen(false);
            }}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </form>

      {showDropdown && (
        <div className="absolute left-0 right-0 top-12 z-50 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-hover dark:border-gray-800 dark:bg-gray-900">
          {isFetching && results.length === 0 ? (
            <p className="p-4 text-sm text-gray-500">{tc("loading")}</p>
          ) : results.length === 0 ? (
            <p className="p-4 text-sm text-gray-500">{tc("noResults")}</p>
          ) : (
            <ul className="max-h-96 overflow-y-auto">
              {results.map((p) => (
                <li key={p.id}>
                  <Link
                    href={`/product/${p.slug}`}
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-3 px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-gray-50 dark:bg-gray-800">
                      {p.image && (
                        <Image src={p.image} alt={p.name} fill sizes="48px" className="object-cover" />
                      )}
                    </div>
                    <span className="line-clamp-1 flex-1 text-sm">{p.name}</span>
                    <span className="shrink-0 text-sm font-bold text-primary">
                      {formatSom(p.final_price)}
                    </span>
                  </Link>
                </li>
              ))}
              <li>
                <button
                  onClick={submit}
                  className="w-full bg-gray-50 px-3 py-2.5 text-center text-sm font-semibold text-primary hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700"
                >
                  {t("search")} →
                </button>
              </li>
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
