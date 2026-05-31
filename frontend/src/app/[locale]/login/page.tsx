"use client";

import { Suspense, useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Link, useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, setTokens } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";

function LoginInner() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const router = useRouter();
  const params = useSearchParams();
  const setUser = useAuth((s) => s.setUser);
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<{ email: string; password: string }>();

  const onSubmit = async (data: { email: string; password: string }) => {
    setLoading(true);
    try {
      const res = await api.post("/auth/login/", data);
      setTokens(res.data.access, res.data.refresh);
      const me = await api.get("/auth/me/");
      setUser(me.data);
      router.push(params.get("next") ?? "/account");
    } catch {
      toast.push(tc("error"), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-zm flex justify-center py-16">
      <div className="w-full max-w-md rounded-3xl border border-gray-100 p-8 shadow-card dark:border-gray-800">
        <h1 className="text-2xl font-extrabold">{t("loginTitle")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("demoHint")}</p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <Input label={t("email")} type="email" {...register("email", { required: true })} />
          <Input label={t("password")} type="password" {...register("password", { required: true })} />
          <Button type="submit" size="lg" className="w-full" disabled={loading}>
            {loading ? tc("loading") : t("loginBtn")}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          {t("noAccount")}{" "}
          <Link href="/register" className="font-semibold text-primary">{t("registerLink")}</Link>
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginInner />
    </Suspense>
  );
}
