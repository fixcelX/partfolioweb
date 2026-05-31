"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { api } from "./api";
import { useAuth } from "@/stores/auth";
import type {
  Address,
  Brand,
  Cart,
  CartItem,
  Category,
  Order,
  Paginated,
  Product,
  ProductDetail,
  Review,
  User,
} from "./types";

// ---------------------------------------------------------------------------
// Optimistik yordamchilar — savat jamlanmasini qayta hisoblash
// ---------------------------------------------------------------------------
function recalcCart(cart: Cart): Cart {
  const total = cart.items.reduce((s, i) => s + Number(i.subtotal || 0), 0);
  const total_quantity = cart.items.reduce((s, i) => s + i.quantity, 0);
  return { ...cart, total: String(total), total_quantity };
}

function emptyCart(): Cart {
  return { id: 0, items: [], total: "0", total_quantity: 0 };
}

// ---------- Catalog ----------
export function useBrands() {
  return useQuery({
    queryKey: ["brands"],
    queryFn: async () =>
      (await api.get<Paginated<Brand>>("/brands/")).data.results,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () =>
      (await api.get<Paginated<Category>>("/categories/")).data.results,
  });
}

export function useProducts(params: Record<string, string | number | undefined>) {
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== ""),
  );
  return useQuery({
    queryKey: ["products", clean],
    queryFn: async () =>
      (await api.get<Paginated<Product>>("/products/", { params: clean })).data,
  });
}

export function useProductFeed(kind: "featured" | "new" | "bestsellers") {
  return useQuery({
    queryKey: ["feed", kind],
    queryFn: async () =>
      (await api.get<Product[]>(`/products/${kind}/`)).data,
  });
}

export function useProduct(slug: string) {
  return useQuery({
    queryKey: ["product", slug],
    queryFn: async () =>
      (await api.get<ProductDetail>(`/products/${slug}/`)).data,
    enabled: !!slug,
  });
}

export function useReviews(slug: string) {
  return useQuery({
    queryKey: ["reviews", slug],
    queryFn: async () =>
      (await api.get<Paginated<Review>>(`/products/${slug}/reviews/`)).data
        .results,
    enabled: !!slug,
  });
}

// ---------- Cart ----------
export function useCart() {
  return useQuery({
    queryKey: ["cart"],
    queryFn: async () => (await api.get<Cart>("/cart/")).data,
  });
}

export function useAddToCart() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      product_id: number;
      quantity?: number;
      product?: Product;
    }) =>
      (
        await api.post<Cart>("/cart/items/", {
          product_id: vars.product_id,
          quantity: vars.quantity ?? 1,
        })
      ).data,
    // Optimistik: UI darhol yangilanadi, server javobini kutmaydi
    onMutate: async (vars) => {
      await qc.cancelQueries({ queryKey: ["cart"] });
      const previous = qc.getQueryData<Cart>(["cart"]);
      if (vars.product) {
        const cart = previous ? { ...previous } : emptyCart();
        const qty = vars.quantity ?? 1;
        const items = [...cart.items];
        const idx = items.findIndex((i) => i.product.id === vars.product_id);
        const unit = Number(vars.product.final_price);
        if (idx >= 0) {
          const it = items[idx];
          const quantity = it.quantity + qty;
          items[idx] = { ...it, quantity, subtotal: String(unit * quantity) };
        } else {
          items.push({
            id: -Date.now(), // vaqtinchalik id
            product: vars.product,
            quantity: qty,
            subtotal: String(unit * qty),
          } as CartItem);
        }
        qc.setQueryData<Cart>(["cart"], recalcCart({ ...cart, items }));
      }
      return { previous };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.previous) qc.setQueryData(["cart"], ctx.previous);
    },
    onSuccess: (data) => qc.setQueryData(["cart"], data),
  });
}

export function useUpdateCartItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: number; quantity: number }) =>
      (
        await api.patch<Cart>(`/cart/items/${vars.id}/`, {
          quantity: vars.quantity,
        })
      ).data,
    onMutate: async (vars) => {
      await qc.cancelQueries({ queryKey: ["cart"] });
      const previous = qc.getQueryData<Cart>(["cart"]);
      if (previous) {
        const items = previous.items.map((i) =>
          i.id === vars.id
            ? {
                ...i,
                quantity: vars.quantity,
                subtotal: String(
                  Number(i.product.final_price) * vars.quantity,
                ),
              }
            : i,
        );
        qc.setQueryData<Cart>(["cart"], recalcCart({ ...previous, items }));
      }
      return { previous };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.previous) qc.setQueryData(["cart"], ctx.previous);
    },
    onSuccess: (data) => qc.setQueryData(["cart"], data),
  });
}

export function useRemoveCartItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/cart/items/${id}/`);
    },
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["cart"] });
      const previous = qc.getQueryData<Cart>(["cart"]);
      if (previous) {
        const items = previous.items.filter((i) => i.id !== id);
        qc.setQueryData<Cart>(["cart"], recalcCart({ ...previous, items }));
      }
      return { previous };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.previous) qc.setQueryData(["cart"], ctx.previous);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["cart"] }),
  });
}

// ---------- Orders ----------
export function useOrders() {
  return useQuery({
    queryKey: ["orders"],
    queryFn: async () =>
      (await api.get<Paginated<Order>>("/orders/")).data.results,
  });
}

export function useCheckout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, string>) =>
      (await api.post<Order>("/orders/", payload)).data,
    onSuccess: () => {
      qc.setQueryData(["cart"], emptyCart());
      qc.invalidateQueries({ queryKey: ["cart"] });
      qc.invalidateQueries({ queryKey: ["orders"] });
    },
  });
}

// ---------- Wishlist ----------
export function useWishlist(enabled = true) {
  return useQuery({
    queryKey: ["wishlist"],
    queryFn: async () => (await api.get<Product[]>("/wishlist/")).data,
    enabled,
  });
}

export function useToggleWishlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      productId: number;
      active: boolean;
      product?: Product;
    }) => {
      if (vars.active) {
        await api.delete(`/wishlist/${vars.productId}/`);
      } else {
        await api.post(`/wishlist/${vars.productId}/`);
      }
      return vars;
    },
    // Optimistik: yurak darhol to'ladi/bo'shaydi
    onMutate: async (vars) => {
      await qc.cancelQueries({ queryKey: ["wishlist"] });
      const previous = qc.getQueryData<Product[]>(["wishlist"]) ?? [];
      let next: Product[];
      if (vars.active) {
        next = previous.filter((p) => p.id !== vars.productId);
      } else {
        const stub = vars.product ?? ({ id: vars.productId } as Product);
        next = [...previous, stub];
      }
      qc.setQueryData<Product[]>(["wishlist"], next);
      return { previous };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.previous) qc.setQueryData(["wishlist"], ctx.previous);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["wishlist"] }),
  });
}

// ---------- Reviews ----------
export function useCreateReview(slug: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { rating: number; text: string }) =>
      (await api.post<Review>(`/products/${slug}/reviews/`, payload)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reviews", slug] });
      qc.invalidateQueries({ queryKey: ["product", slug] });
    },
  });
}

// ---------- Account: profil ----------
export function useUpdateProfile() {
  return useMutation({
    mutationFn: async (payload: Partial<Pick<User, "first_name" | "last_name" | "phone">>) =>
      (await api.patch<User>("/auth/me/", payload)).data,
    onSuccess: (user) => {
      // Auth store'dagi foydalanuvchini ham yangilaymiz
      useAuth.getState().setUser(user);
    },
  });
}

// ---------- Account: manzillar ----------
export function useAddresses(enabled = true) {
  return useQuery({
    queryKey: ["addresses"],
    queryFn: async () =>
      (await api.get<Paginated<Address> | Address[]>("/auth/addresses/")).data,
    select: (data) => (Array.isArray(data) ? data : data.results),
    enabled,
  });
}

export function useCreateAddress() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Omit<Address, "id">) =>
      (await api.post<Address>("/auth/addresses/", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["addresses"] }),
  });
}

export function useDeleteAddress() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/auth/addresses/${id}/`);
    },
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["addresses"] });
      const previous = qc.getQueryData<Address[]>(["addresses"]);
      if (previous) {
        qc.setQueryData<Address[]>(
          ["addresses"],
          previous.filter((a) => a.id !== id),
        );
      }
      return { previous };
    },
    onError: (_e, _v, ctx) => {
      if (ctx?.previous) qc.setQueryData(["addresses"], ctx.previous);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["addresses"] }),
  });
}

export function useSetDefaultAddress() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) =>
      (await api.patch<Address>(`/auth/addresses/${id}/`, { is_default: true }))
        .data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["addresses"] }),
  });
}
