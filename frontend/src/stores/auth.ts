"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/lib/types";
import { clearTokens, setTokens } from "@/lib/api";

interface AuthState {
  user: User | null;
  hydrated: boolean;
  setAuth: (user: User, access: string, refresh: string) => void;
  setUser: (user: User | null) => void;
  setHydrated: () => void;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      hydrated: false,
      setAuth: (user, access, refresh) => {
        setTokens(access, refresh);
        set({ user });
      },
      setUser: (user) => set({ user }),
      setHydrated: () => set({ hydrated: true }),
      logout: () => {
        clearTokens();
        set({ user: null });
      },
    }),
    {
      name: "zm-auth",
      partialize: (s) => ({ user: s.user }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated();
      },
    },
  ),
);
