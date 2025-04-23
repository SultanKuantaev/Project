from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# Basic registration of models in the Django admin site

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Auto-populate slug from name

class OrderItemInline(admin.TabularInline): # Display items directly within the Order admin page
    model = OrderItem
    raw_id_fields = ['product'] # Use a popup to select product for large numbers of products
    readonly_fields = ('price_at_purchase',) # Show price, but don't allow editing here
    extra = 1 # Show one empty inline form by default

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock') # Allow editing price/stock directly in the list view

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'created_at') # Add 'status' if implemented
    list_filter = ('created_at',) # Add 'status' if implemented
    search_fields = ('id', 'customer__username', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'total_price') # Calculated/automatic fields
    inlines = [OrderItemInline] # Show related order items

# Simple registration for OrderItem if needed directly (usually handled via Order inline)
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'price_at_purchase')
#     list_filter = ('order__created_at', 'product__category') # Filter by related fields