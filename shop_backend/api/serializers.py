from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password # For stronger validation
from .models import Category, Product, Order, OrderItem

# Serializer 1: Plain Serializer (for Login payload validation)
class LoginSerializer(serializers.Serializer):
    """
    Validates username and password for login.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True, # Don't include password in serialized output
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        # Basic presence check, authentication done in view
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return attrs

# Serializer 2: Plain Serializer (for Registration payload validation and user creation)
class RegisterSerializer(serializers.Serializer):
    """
    Validates registration data and creates a new user.
    """
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password]) # Use Django's validator
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already taken."})

        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email address already registered."})

        return data

    def create(self, validated_data):
        # Create the user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'] # create_user handles hashing
        )
        # Note: We don't use password_confirm here, it's just for validation
        return user


# --- Model Serializers ---

# ModelSerializer 1: Category
class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


# ModelSerializer 2: Product (Includes nested Category details for reading)
class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    Includes nested read-only Category details.
    Uses category_id for writing relationships.
    """
    # Nested serializer for displaying category info (read-only in this context)
    category = CategorySerializer(read_only=True)

    # Field for accepting category ID when creating/updating a product
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',      # Maps this field to the 'category' model field
        write_only=True         # Only used for input, not included in output representation
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'image_url',
            'category',      # Read-only nested representation
            'category_id',   # Write-only ID field
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] # These are set automatically

# --- Order Serializers ---

# ModelSerializer 3: OrderItem (Used within OrderSerializer)
class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    Includes nested read-only Product details for display.
    Uses product_id for associating during creation.
    """
    # Read-only nested representation of the product in an order item
    # Depth could be used, but explicit serializer gives more control
    product = ProductSerializer(read_only=True)

    # Write-only field to accept the product ID when creating order items
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',      # Map to the 'product' field on the OrderItem model
        write_only=True
    )

    # Read-only calculated field (example, if needed, usually done in Order)
    # item_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_item_total')

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',          # Read-only nested product
            'product_id',       # Write-only ID
            'quantity',
            'price_at_purchase',
            # 'item_total'      # Uncomment if calculated field is needed here
        ]
        read_only_fields = ['price_at_purchase'] # Price is set automatically on save/creation


# ModelSerializer 4: Order (Handles listing and creating orders with nested items)
class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. Handles nested creation/listing of OrderItems.
    """
    # Nested serializer for items within an order. Handles multiple items.
    items = OrderItemSerializer(many=True)
    # Display the customer's username, prevent modification through this serializer
    customer = serializers.ReadOnlyField(source='customer.username')
    # You could also include full customer details if needed:
    # customer = UserSerializer(read_only=True) # Assuming UserSerializer exists

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',         # Read-only username
            'created_at',
            'items',            # Nested list of order items
            'total_price',      # Calculated total price
            # 'status',         # Include if status field is added to Order model
        ]
        # Total price is calculated server-side during creation/update
        read_only_fields = ['total_price', 'created_at']

    def create(self, validated_data):
        """
        Handles creation of an Order and its associated OrderItems.
        Links the order to the authenticated user provided in the context.
        """
        items_data = validated_data.pop('items') # Extract nested item data
        # Get the customer (authenticated user) from the view context
        customer = self.context['request'].user

        # Create the Order instance, linked to the customer
        order = Order.objects.create(customer=customer, **validated_data)

        order_total_price = 0
        # Create each OrderItem associated with the newly created Order
        for item_data in items_data:
            product_instance = item_data.pop('product') # Get Product instance from validated data
            quantity = item_data.get('quantity')

            # Basic stock check before creating item
            if product_instance.stock >= quantity:
                 item = OrderItem.objects.create(
                    order=order,
                    product=product_instance,
                    # Price at purchase is set automatically by OrderItem's save method
                    **item_data
                )
                 # Decrease stock (simple implementation - consider race conditions in high-traffic scenarios)
                 # product_instance.stock -= quantity
                 # product_instance.save(update_fields=['stock']) # Only update stock

                 # Accumulate total price using price_at_purchase set on item creation
                 order_total_price += item.price_at_purchase * item.quantity
            else:
                 # Handle insufficient stock: either raise validation error or skip item
                 # Option 1: Raise error immediately (stops order creation)
                 order.delete() # Clean up the partially created order
                 raise serializers.ValidationError(
                    f"Insufficient stock for product '{product_instance.name}'. Available: {product_instance.stock}, Requested: {quantity}."
                 )
                 # Option 2: Skip item and potentially notify user (more complex)
                 # print(f"Warning: Insufficient stock for {product_instance.name}. Item not added to order.")
                 # continue

        # Update the order's total price
        order.total_price = order_total_price
        order.save(update_fields=['total_price'])

        # --- Stock Update (Alternative location - after all items processed) ---
        # It might be better to validate all stock first, then create order, then decrement stock
        for item in order.items.all():
             product = item.product
             product.stock -= item.quantity
             product.save(update_fields=['stock'])
        # --- End Stock Update ---

        return order