from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.CharField(max_length=200, blank=True)  # URL to image
    
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    SIZES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    COLORS = [
        ('black', 'Black'),
        ('white', 'White'),
        ('red', 'Red'),
        ('blue', 'Blue'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZES)
    color = models.CharField(max_length=10, choices=COLORS)
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.product.name} - {self.size}-{self.color}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.variant} x {self.quantity}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Add this
    
    # For guest checkout (no login required)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=10)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    
    # Order details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    variant_text = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.user.username}"

from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount (₹)'),
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(default=100)
    times_used = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.code} - {self.discount_value} {self.discount_type}"
    
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and 
                self.times_used < self.max_uses)
    
    def get_discount_amount(self, total):
        if self.discount_type == 'percentage':
            return (total * self.discount_value) / 100
        else:
            return self.discount_value


