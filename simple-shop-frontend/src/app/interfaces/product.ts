export interface Category {
    id: number;
    name: string;
    slug: string;
  }
  
  export interface Product {
    id: number;
    name: string;
    description: string;
    price: string;
    stock: number;
    image_url?: string | null;
    category: Category;
    created_at: string;
    updated_at: string;
  }