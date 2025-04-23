import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { CartItem } from '../interfaces/cart';
import { Product } from '../interfaces/product';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({ providedIn: 'root' })
export class CartService {
  private storageKey = 'shoppingCart';
  private _cartItems = new BehaviorSubject<CartItem[]>(this.loadCart());
  cartItems$ = this._cartItems.asObservable();

  private _itemCount = new BehaviorSubject<number>(0);
  itemCount$ = this._itemCount.asObservable();

  private _totalPrice = new BehaviorSubject<number>(0);
  totalPrice$ = this._totalPrice.asObservable();

  constructor(private snackBar: MatSnackBar) {
    this.updateCartState();
  }

  addToCart(product: Product, quantity: number = 1): void {
    const currentItems = this._cartItems.getValue();
    const existingItemIndex = currentItems.findIndex(item => item.product.id === product.id);
    let message = '';

    if (product.stock <= 0 && existingItemIndex === -1) {
       message = `${product.name} is out of stock. Cannot add to cart.`;
       this.snackBar.open(message, 'Close', { duration: 3000 });
       return; // Don't add if out of stock from start
    }

    if (existingItemIndex > -1) {
       const existingItem = currentItems[existingItemIndex];
       const newQuantity = existingItem.quantity + quantity;
       if(newQuantity <= product.stock) {
           existingItem.quantity = newQuantity;
           message = `${quantity} more ${product.name}(s) added. Total: ${newQuantity}.`;
       } else if (existingItem.quantity < product.stock) {
           const added = product.stock - existingItem.quantity;
           existingItem.quantity = product.stock;
           message = `Added ${added} more ${product.name}(s) (Max stock: ${product.stock}).`;
       } else {
           message = `Max stock (${product.stock}) for ${product.name} already in cart.`;
       }
    } else { // Add new item
       const quantityToAdd = Math.min(quantity, product.stock);
       currentItems.push({ product, quantity: quantityToAdd });
       message = `${quantityToAdd} ${product.name}(s) added to cart.`;
       if (quantity > product.stock) {
           message += ` Requested ${quantity}, but only ${product.stock} in stock.`;
       }
    }

    this._cartItems.next([...currentItems]);
    this.updateCartState();
    this.saveCart();
    this.snackBar.open(message, 'Close', { duration: 3000 });
  }

  removeFromCart(productId: number): void {
    let productName = 'Item';
    const updatedItems = this._cartItems.getValue().filter(item => {
      if (item.product.id === productId) {
        productName = item.product.name;
        return false; // Exclude item
      }
      return true; // Keep item
    });
    this._cartItems.next(updatedItems);
    this.updateCartState();
    this.saveCart();
    this.snackBar.open(`${productName} removed.`, 'Close', { duration: 2000 });
  }

  updateQuantity(productId: number, quantity: number): void {
      const currentItems = this._cartItems.getValue();
      const itemIndex = currentItems.findIndex(item => item.product.id === productId);

      if(itemIndex > -1) {
          const item = currentItems[itemIndex];
          const validQuantity = Math.max(0, Math.min(quantity, item.product.stock)); // Clamp between 0 and stock

          if(validQuantity > 0) {
              if(item.quantity !== validQuantity){
                 item.quantity = validQuantity;
                 if (quantity > item.product.stock) {
                     this.snackBar.open(`Max stock for ${item.product.name} is ${item.product.stock}.`, 'Close', { duration: 3000 });
                 }
              }
          } else {
             currentItems.splice(itemIndex, 1); // Remove if quantity becomes 0
             this.snackBar.open(`${item.product.name} removed from cart.`, 'Close', { duration: 2000 });
          }

          this._cartItems.next([...currentItems]);
          this.updateCartState();
          this.saveCart();
      }
  }


  clearCart(): void {
    this._cartItems.next([]);
    this.updateCartState();
    if (typeof localStorage !== 'undefined') localStorage.removeItem(this.storageKey);
    this.snackBar.open('Cart cleared.', 'Close', { duration: 2000 });
  }

  private updateCartState(): void {
    const items = this._cartItems.getValue();
    this._itemCount.next(items.reduce((sum, item) => sum + item.quantity, 0));
    this._totalPrice.next(
      items.reduce((sum, item) => sum + parseFloat(item.product.price) * item.quantity, 0)
    );
  }

  private saveCart(): void {
     if (typeof localStorage !== 'undefined') {
         localStorage.setItem(this.storageKey, JSON.stringify(this._cartItems.getValue()));
     }
  }

  private loadCart(): CartItem[] {
     if (typeof localStorage !== 'undefined') {
        const savedCart = localStorage.getItem(this.storageKey);
        return savedCart ? JSON.parse(savedCart) : [];
     }
     return [];
  }

  getCurrentCartItems(): CartItem[] { // Helper to get snapshot for order placement
    return this._cartItems.getValue();
  }
}