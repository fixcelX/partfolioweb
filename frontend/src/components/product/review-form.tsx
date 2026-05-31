"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useCreateReview } from "@/lib/hooks";
import { useAuth } from "@/stores/auth";
import { cn } from "@/lib/utils";

export function ReviewForm({ slug }: { slug: string }) {
  const t = useTranslations("product");
  const tc = useTranslations("common");
  const user = useAuth((s) => s.user);
  const toast = useToast();
  const create = useCreateReview(slug);
  const [rating, setRating] = useState(5);
  const [hover, setHover] = useState(0);
  const [text, setText] = useState("");

  if (!user) {
    return (
      <div className="rounded-xl border border-dashed border-gray-200 p-5 text-center text-sm text-gray-500 dark:border-gray-700">
        <Link href="/login" className="font-semibold text-primary hover:underline">
          {t("loginToReview")}
        </Link>
      </div>
    );
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    create.mutate(
      { rating, text },
      {
        onSuccess: () => {
          toast.push(t("reviewThanks"));
          setText("");
          setRating(5);
        },
        onError: (err: unknown) => {
          const msg =
            (err as { response?: { data?: { detail?: string } } })?.response?.data
              ?.detail ?? tc("error");
          toast.push(msg, "error");
        },
      },
    );
  };

  return (
    <form onSubmit={submit} className="rounded-xl border border-gray-100 p-5 dark:border-gray-800">
      <p className="mb-2 text-sm font-semibold">{t("yourRating")}</p>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <button
            key={i}
            type="button"
            onClick={() => setRating(i)}
            onMouseEnter={() => setHover(i)}
            onMouseLeave={() => setHover(0)}
          >
            <Star
              className={cn(
                "h-7 w-7 transition",
                i <= (hover || rating)
                  ? "fill-warning text-warning"
                  : "fill-gray-200 text-gray-200 dark:fill-gray-700 dark:text-gray-700",
              )}
            />
          </button>
        ))}
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={t("reviewText")}
        rows={3}
        className="mt-3 w-full rounded-xl border border-gray-200 p-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-700 dark:bg-gray-800"
      />
      <Button type="submit" className="mt-3" disabled={create.isPending}>
        {create.isPending ? tc("loading") : t("submitReview")}
      </Button>
    </form>
  );
}
