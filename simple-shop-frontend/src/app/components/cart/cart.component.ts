import { Component } from '@angular/core';
import { CartService } from '../../services/cart.service';
import { CartItem } from '../../interfaces/cart'; // <<< CORRECTED: Import from interfaces
import { OrderService } from '../../services/order.service';
import { AuthService } from '../../services/auth.service';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-cart',
  standalone: false,
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent {
  cartItems$: Observable<CartItem[]>;
  cartItemCount$: Observable<number>;
  cartTotalPrice$: Observable<number>;
  isLoggedIn$: Observable<boolean>;

  isLoading = false; // For place order button
  orderError: string | null = null;
  orderSuccess: string | null = null;

  // Make parseFloat available in template
  parseFloat = parseFloat;

  constructor(
    private cartService: CartService,
    private orderService: OrderService,
    private authService: AuthService,
    private router: Router
  ) {
    this.cartItems$ = this.cartService.cartItems$;
    this.cartItemCount$ = this.cartService.itemCount$;
    this.cartTotalPrice$ = this.cartService.totalPrice$;
    this.isLoggedIn$ = this.authService.isAuthenticated$;
  }

  // Called by [(ngModel)] or (input) change event
  updateQuantity(productId: number, quantityEvent: any): void {
     // Input type=number can return string or number
     const quantity = Number(quantityEvent);
     if (!isNaN(quantity)) {
         this.cartService.updateQuantity(productId, quantity);
     }
  }

  // Click Event 5 (interacts with CartService)
  removeFromCart(productId: number): void {
    this.cartService.removeFromCart(productId);
  }

  // Click Event 6 (interacts with CartService)
  clearCart(): void {
      this.cartService.clearCart();
  }

  // Click Event 7 (Makes API call via OrderService)
  placeOrder(): void {
    this.orderError = null;
    this.orderSuccess = null;

    // Ensure user is logged in (though Guard should prevent reaching here if not)
    this.isLoggedIn$.pipe(take(1)).subscribe(loggedIn => {
      if (!loggedIn) {
        this.orderError = "Please log in to place an order.";
        this.router.navigate(['/login'], { queryParams: { returnUrl: '/cart' } });
        return;
      }

      const currentCartItems = this.cartService.getCurrentCartItems(); // Get snapshot
      if (currentCartItems.length === 0) {
        this.orderError = "Cannot place order with an empty cart.";
        return;
      }

      this.isLoading = true;
      this.orderService.createOrder(currentCartItems).subscribe({
        next: (order) => {
          this.isLoading = false;
          this.orderSuccess = `Order #${order.id} placed successfully!`;
          this.cartService.clearCart(); // Clear cart after successful order
          setTimeout(() => this.router.navigate(['/orders']), 2000); // Redirect after short delay
        },
        error: (err) => {
          this.isLoading = false;
          this.orderError = err.message || 'Failed to place order.';
          console.error('Order placement error:', err);
        }
      });
    });
  }
}

// Need import for take(1)
import { take } from 'rxjs/operators';