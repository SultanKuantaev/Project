# api/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    # We are using custom login view, so commented out default JWT view
    # TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # --- Authentication Endpoints ---
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    # Use this endpoint to get a new access token using a valid refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Logout is typically handled client-side by deleting tokens

    # --- Product Endpoints ---
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # --- Category Endpoints ---
    # Example using generic view
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    # If you implemented Category Detail/Create views, add them here

    # --- Order Endpoints (CRUD Example) ---
    path('orders/', views.OrderListCreateView.as_view(), name='order-list-create'),
    # Optional: Add Order Detail endpoint if you created the view
    # path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]