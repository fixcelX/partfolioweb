"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/routing";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, setTokens } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";

interface FormData {
  first_name: string;
  email: string;
  password: string;
  password2: string;
}

export default function RegisterPage() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const router = useRouter();
  const setAuth = useAuth((s) => s.setAuth);
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const res = await api.post("/auth/register/", data);
      setAuth(res.data.user, res.data.access, res.data.refresh);
      setTokens(res.data.access, res.data.refresh);
      router.push("/account");
    } catch (e: unknown) {
      const errors = (e as { response?: { data?: { errors?: Record<string, string[]> } } })
        ?.response?.data?.errors;
      const first = errors ? Object.values(errors)[0]?.[0] : tc("error");
      toast.push(first ?? tc("error"), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-zm flex justify-center py-16">
      <div className="w-full max-w-md rounded-3xl border border-gray-100 p-8 shadow-card dark:border-gray-800">
        <h1 className="text-2xl font-extrabold">{t("registerTitle")}</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <Input label={t("firstName")} {...register("first_name", { required: true })} />
          <Input label={t("email")} type="email" {...register("email", { required: true })} />
          <Input label={t("password")} type="password" {...register("password", { required: true })} />
          <Input label={t("passwordConfirm")} type="password" {...register("password2", { required: true })} />
          <Button type="submit" size="lg" className="w-full" disabled={loading}>
            {loading ? tc("loading") : t("registerBtn")}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          {t("haveAccount")}{" "}
          <Link href="/login" className="font-semibold text-primary">{t("loginLink")}</Link>
        </p>
      </div>
    </div>
  );
}
