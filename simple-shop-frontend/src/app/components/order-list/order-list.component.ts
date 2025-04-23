import { Component, OnInit } from '@angular/core';
import { OrderService } from '../../services/order.service';
import { Order } from '../../interfaces/order'; // <<< CORRECTED: Import from interfaces

@Component({
  selector: 'app-order-list',
  standalone: false,
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.css']
})
export class OrderListComponent implements OnInit {
  orders: Order[] = [];
  isLoading = true;
  errorMessage: string | null = null;
  parseFloat = parseFloat; // Make available in template

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  // API call happens on component init
  loadOrders(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.orderService.getOrders().subscribe({
      next: (data) => {
        this.orders = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = err.message || 'Failed to load orders.';
        this.isLoading = false;
        console.error('Error loading orders:', err);
      }
    });
  }
}