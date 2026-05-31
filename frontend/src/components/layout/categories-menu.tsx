"use client";

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { useCategories } from "@/lib/hooks";

export function CategoriesMenu({ onClose }: { onClose: () => void }) {
  const { data: categories } = useCategories();
  const t = useTranslations("home");

  return (
    <>
      <div className="fixed inset-0 top-16 z-30 bg-black/20" onClick={onClose} />
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute inset-x-0 z-40 border-b border-gray-100 bg-white shadow-hover dark:border-gray-800 dark:bg-gray-950"
      >
        <div className="container-zm grid grid-cols-2 gap-x-8 gap-y-4 py-6 md:grid-cols-4">
          {categories?.map((cat) => (
            <div key={cat.id}>
              <Link
                href={`/category/${cat.slug}`}
                onClick={onClose}
                className="font-bold text-gray-900 hover:text-primary dark:text-white"
              >
                {cat.name}
              </Link>
              <ul className="mt-2 space-y-1.5">
                {cat.children.map((child) => (
                  <li key={child.id}>
                    <Link
                      href={`/category/${child.slug}`}
                      onClick={onClose}
                      className="text-sm text-gray-600 hover:text-primary dark:text-gray-400"
                    >
                      {child.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </motion.div>
    </>
  );
}
