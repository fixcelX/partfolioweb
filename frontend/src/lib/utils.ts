import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Narxni so'mda formatlash: 1 250 000 so'm */
export function formatSom(value: string | number): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 })
    .format(Math.round(num))
    .replace(/,/g, " ");
}
