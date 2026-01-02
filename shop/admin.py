from django.contrib import admin
from .models import Category, Product, ProductVariant, CartItem, Order, OrderItem , Review , Coupon

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Coupon)