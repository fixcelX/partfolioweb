"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Check, X } from "lucide-react";
import { create } from "zustand";

interface Toast {
  id: number;
  message: string;
  type: "success" | "error";
}

interface ToastState {
  toasts: Toast[];
  push: (message: string, type?: "success" | "error") => void;
  remove: (id: number) => void;
}

export const useToast = create<ToastState>((set) => ({
  toasts: [],
  push: (message, type = "success") => {
    const id = Date.now() + Math.random();
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(
      () => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
      2800,
    );
  },
  remove: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

export function Toaster() {
  const { toasts, remove } = useToast();
  return (
    <div className="fixed bottom-5 right-5 z-[100] flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, x: 40, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 40, scale: 0.9 }}
            className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white shadow-hover ${
              t.type === "success" ? "bg-success" : "bg-danger"
            }`}
          >
            <span className="rounded-full bg-white/20 p-1">
              {t.type === "success" ? (
                <Check className="h-3.5 w-3.5" />
              ) : (
                <X className="h-3.5 w-3.5" />
              )}
            </span>
            {t.message}
            <button onClick={() => remove(t.id)} className="ml-2 opacity-70">
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
