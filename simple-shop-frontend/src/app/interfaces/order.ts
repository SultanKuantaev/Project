import { Product } from './product';

export interface OrderItemPayload {
  product_id: number;
  quantity: number;
}

export interface OrderPayload {
  items: OrderItemPayload[];
}

export interface OrderItem {
    id: number;
    product: Product;
    quantity: number;
    price_at_purchase: string;
}

export interface Order {
    id: number;
    customer: string;
    created_at: string;
    items: OrderItem[];
    total_price: string;
}