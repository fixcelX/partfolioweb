export interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;
  image: string | null;
  order: number;
  children: Category[];
  products_count?: number;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  logo: string | null;
}

export interface ProductImage {
  id: number;
  src: string;
  alt: string;
  order: number;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  price: string;
  discount_price: string | null;
  final_price: string;
  discount_percent: number;
  rating: string;
  reviews_count: number;
  sold_count: number;
  stock: number;
  in_stock: boolean;
  is_featured: boolean;
  image: string | null;
}

export interface ProductDetail extends Product {
  description: string;
  images: ProductImage[];
  category: Category;
  brand: Brand | null;
  sku: string;
  similar: Product[];
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  subtotal: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total: string;
  total_quantity: number;
}

export interface OrderItem {
  id: number;
  product_slug: string;
  product_name: string;
  price: string;
  quantity: number;
  subtotal: string;
}

export type OrderStatus =
  | "pending"
  | "paid"
  | "shipped"
  | "delivered"
  | "cancelled";

export interface Order {
  id: number;
  number: string;
  status: OrderStatus;
  status_display: string;
  payment_method: string;
  full_name: string;
  phone: string;
  region: string;
  city: string;
  street: string;
  total: string;
  items: OrderItem[];
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  avatar: string | null;
  role: string;
}

export interface Address {
  id: number;
  full_name: string;
  phone: string;
  region: string;
  city: string;
  street: string;
  zip_code: string;
  is_default: boolean;
}

export interface Review {
  id: number;
  user_name: string;
  rating: number;
  text: string;
  is_verified: boolean;
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
