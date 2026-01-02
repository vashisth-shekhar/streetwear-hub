from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<int:index>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:index>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.profile, name='profile'),
]
