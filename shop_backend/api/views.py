from django.contrib.auth import authenticate
from django.contrib.auth.models import User # Import User model if needed directly
from django.shortcuts import get_object_or_404 # For detail views if not using APIView helper

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product, Category, Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer, OrderSerializer, OrderItemSerializer, # Include OrderItemSerializer if used directly
    LoginSerializer, RegisterSerializer
)

# --- Function-Based Views (FBV) for Authentication ---

# FBV 1: User Registration
@api_view(['POST'])
@permission_classes([permissions.AllowAny]) # Anyone can register
def register_user(request):
    """
    Handles user registration requests.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        # create() method in serializer handles user creation
        user = serializer.save()
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': { # Return basic user info upon successful registration
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
    # Return validation errors if data is invalid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FBV 2: User Login
@api_view(['POST'])
@permission_classes([permissions.AllowAny]) # Anyone can attempt login
def login_user(request):
    """
    Handles user login requests and returns JWT tokens upon success.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Authentication successful, generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': { # Return basic user info upon successful login
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    # Return validation errors if input format is wrong (e.g., missing fields)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Class-Based Views (CBV using APIView) for Resources ---

# CBV 1 & 2: Product List (GET) and Create (POST)
class ProductListCreateView(APIView):
    """
    List all products (GET, AllowAny) or create a new product (POST, Admin only).
    """
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Overrides default to apply different permissions based on method.
        """
        if self.request.method == 'POST':
            # Only Admins (or superusers) can create products
            return [permissions.IsAdminUser()]
        # Anyone can view the list of products
        return [permissions.AllowAny()]

    def get(self, request, format=None):
        """ Return a list of all products. """
        products = Product.objects.select_related('category').all() # Optimize query
        # Apply filtering/searching here if needed (e.g., request.query_params)
        # category_slug = request.query_params.get('category')
        # if category_slug:
        #     products = products.filter(category__slug=category_slug)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """ Create a new product. """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() # Creates the product instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# CBV 3: Product Detail (GET), Update (PUT), Delete (DELETE)
class ProductDetailView(APIView):
    """
    Retrieve (GET), update (PUT), or delete (DELETE) a product instance.
    """
    def get_permissions(self):
        """ Admins can modify/delete, anyone can view details. """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_object(self, pk):
        """ Helper method to get the product object or raise 404. """
        try:
            # Fetch product with related category to avoid extra queries if needed by serializer
            return Product.objects.select_related('category').get(pk=pk)
        except Product.DoesNotExist:
            # Use DRF's standard exception handling which maps to 404
            raise status.HTTP_404_NOT_FOUND
            # Alternatively: from django.http import Http404; raise Http404

    def get(self, request, pk, format=None):
        """ Retrieve a specific product by its ID. """
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Update an existing product. (PUT requires all fields)"""
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data) # Pass instance for update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Optional: Add PATCH method for partial updates
    # def patch(self, request, pk, format=None):
    #     """ Partially update an existing product. """
    #     product = self.get_object(pk)
    #     serializer = ProductSerializer(product, data=request.data, partial=True) # partial=True
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """ Delete a product. """
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) # Success, no content to return

# CBV 4 & 5: Order List (GET) and Create (POST) - Full CRUD example on Order model
class OrderListCreateView(APIView):
    """
    List user's orders (GET) or create a new order (POST).
    Requires authentication for both actions.
    """
    permission_classes = [permissions.IsAuthenticated] # User must be logged in

    def get(self, request, format=None):
        """ Retrieve orders placed by the currently authenticated user. """
        # Filter orders to only those belonging to the request user
        orders = Order.objects.filter(customer=request.user).prefetch_related(
            'items', 'items__product' # Optimize query to fetch related items and their products
        ).order_by('-created_at') # Show most recent first
        serializer = OrderSerializer(orders, many=True, context={'request': request}) # Pass context if serializer needs it
        return Response(serializer.data)

    def post(self, request, format=None):
        """ Create a new order for the authenticated user based on cart data. """
        serializer = OrderSerializer(data=request.data, context={'request': request}) # Pass request context to serializer
        if serializer.is_valid():
            # Serializer's create method handles saving the order and items,
            # and links it to the user from the context.
            # It also calculates total_price and updates stock.
            serializer.save() # No need to pass customer here, done in serializer's create
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Return errors from the serializer (e.g., validation, stock issues)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Optional: Example using Generic Views for simpler listing (if APIView wasn't strictly required)
class CategoryListView(generics.ListAPIView):
     """ List all categories (GET, AllowAny) """
     queryset = Category.objects.all().order_by('name')
     serializer_class = CategorySerializer
     permission_classes = [permissions.AllowAny] # Anyone can view categories


# You could add OrderDetailView (APIView or generic RetrieveUpdateDestroyAPIView)
# to allow viewing, updating (e.g., status), or deleting specific orders,
# potentially restricted to the owner or admins. Example structure:
#
# class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated] # Add IsOwnerOrAdmin permission if needed
#
#     def get_queryset(self):
#         """ Ensure users can only access their own orders. """
#         return Order.objects.filter(customer=self.request.user)
#
#     # You might override update/destroy methods for custom logic (e.g., disallow deleting shipped orders)