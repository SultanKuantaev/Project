import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { Product } from '../../interfaces/product'; // <<< CORRECTED: Import from interfaces
import { CartService } from '../../services/cart.service'; // Import CartService

@Component({
  selector: 'app-product-list',
  standalone: false,
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent implements OnInit {
  products: Product[] = [];
  isLoading = true;
  errorMessage: string | null = null;

  constructor(
    private productService: ProductService,
    private cartService: CartService // Inject CartService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  // API call happens on component init (driven by user navigating here)
  loadProducts(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.productService.getProducts().subscribe({
      next: (data) => {
        this.products = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading products:', err);
        this.errorMessage = 'Failed to load products. Please try again later.';
        this.isLoading = false;
      }
    });
  }

  // Click Event 4 (Does NOT directly call API, interacts with CartService)
  addToCart(product: Product): void {
    console.log('Adding to cart:', product);
    this.cartService.addToCart(product);
    // Notification handled within CartService now
  }
}