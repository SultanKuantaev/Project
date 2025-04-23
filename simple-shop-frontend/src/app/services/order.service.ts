import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Order, OrderPayload } from '../interfaces/order';
import { CartItem } from '../interfaces/cart';

@Injectable({ providedIn: 'root' })
export class OrderService {
  private apiUrl = `${environment.apiUrl}/orders/`;

  constructor(private http: HttpClient) {}

  getOrders(): Observable<Order[]> { // API CALL 1 (GET on init/nav)
    return this.http.get<Order[]>(this.apiUrl).pipe(catchError(this.handleError));
  }

  createOrder(cartItems: CartItem[]): Observable<Order> { // API CALL 2 (POST on button click)
    const payload: OrderPayload = {
      items: cartItems.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
      }))
    };
    return this.http.post<Order>(this.apiUrl, payload).pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred!';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      console.error(`Backend error: ${error.status}`, error.error);
      if (error.status === 401) {
        errorMessage = 'Authorization Error. Please log in again.';
        // Consider calling authService.logout() here if needed globally
      } else if (error.status === 400 && error.error) {
        errorMessage = Object.values(error.error).flat().join(' ') || 'Invalid data submitted.';
      } else if (error.status === 0) {
           errorMessage = 'Could not connect to the server. Is it running?';
      }
       else {
        errorMessage = `Server returned code ${error.status}.`;
      }
    }
    return throwError(() => new Error(errorMessage));
  }
}