from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Model 1: Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True) # Useful for URLs

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

# Model 2: Product
class Product(models.Model):
    # ForeignKey 1: Product belongs to a Category
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # Simple image handling
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        # Add index for faster lookups if needed
        # indexes = [
        #     models.Index(fields=['name']),
        # ]

# Model 3: Order
class Order(models.Model):
    # ForeignKey 2: Order belongs to a User (Customer)
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Could add status field ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
    # status = models.CharField(max_length=20, default='Pending', choices=[...])

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"

    class Meta:
        ordering = ['-created_at']

# Model 4: OrderItem (Connects Order and Product, many-to-many relationship through this model)
class OrderItem(models.Model):
    # ForeignKey 3: Item belongs to an Order
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # ForeignKey 4: Item references a Product
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Store the price at the time of purchase in case the product price changes later
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # Allow blank initially

    def save(self, *args, **kwargs):
        # Set price at purchase time if it hasn't been set (e.g., on create)
        if self.pk is None and not self.price_at_purchase and self.product:
             self.price_at_purchase = self.product.price
        elif self.price_at_purchase is None and self.product: # Allow updates if needed, but maybe unusual
             self.price_at_purchase = self.product.price
        super().save(*args, **kwargs)

    def get_item_total(self):
        # Calculate the total for this line item
        if self.price_at_purchase is not None:
            return self.price_at_purchase * self.quantity
        return 0 # Or handle error/default case

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

    class Meta:
        # Prevent adding the same product multiple times to the same order; update quantity instead
        unique_together = ('order', 'product')