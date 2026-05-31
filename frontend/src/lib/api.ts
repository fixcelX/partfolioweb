import axios from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // anonim savat uchun sessiya cookie
});

const ACCESS_KEY = "zm_access";
const REFRESH_KEY = "zm_refresh";

export function setTokens(access: string, refresh?: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function getAccess(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

// Har so'rovga access token + til qo'shish
api.interceptors.request.use((config) => {
  const token = getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (typeof document !== "undefined") {
    const locale = document.documentElement.lang || "uz";
    config.headers["Accept-Language"] = locale;
  }
  return config;
});

// 401 bo'lsa refresh urinish
let refreshing: Promise<string | null> | null = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh =
        typeof window !== "undefined"
          ? localStorage.getItem(REFRESH_KEY)
          : null;
      if (!refresh) return Promise.reject(error);
      try {
        refreshing =
          refreshing ??
          axios
            .post(`${API_URL}/auth/refresh/`, { refresh })
            .then((r) => {
              setTokens(r.data.access);
              return r.data.access as string;
            })
            .finally(() => {
              refreshing = null;
            });
        const newAccess = await refreshing;
        if (newAccess) {
          original.headers.Authorization = `Bearer ${newAccess}`;
          return api(original);
        }
      } catch {
        clearTokens();
      }
    }
    return Promise.reject(error);
  },
);
