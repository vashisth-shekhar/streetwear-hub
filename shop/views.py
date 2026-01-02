from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Product, ProductVariant, Order, OrderItem, Category

def home(request):
    return render(request, 'shop/home.html')

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Search by product name
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__id=category_filter)
    
    # Filter by price range
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'min_price': min_price,
        'max_price': max_price,
    })

def product_detail(request, id):
    product = Product.objects.get(id=id)
    variants = product.productvariant_set.all()
    
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        
        if variant_id:
            if 'cart' not in request.session:
                request.session['cart'] = []
            
            variant = ProductVariant.objects.get(id=variant_id)
            
            request.session['cart'].append({
                'product_id': product.id,
                'product_name': product.name,
                'variant_id': variant_id,
                'variant_text': f"{variant.get_size_display()}-{variant.get_color_display()}",
                'price': str(product.price),
                'quantity': 1
            })
            request.session.modified = True
            return redirect('cart_view')
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'variants': variants
    })

def cart_view(request):
    cart = request.session.get('cart', [])
    total = sum(float(item['price']) * item['quantity'] for item in cart)
    
    return render(request, 'shop/cart.html', {
        'cart': cart,
        'total': total,
        'cart_count': len(cart)
    })

def remove_from_cart(request, index):
    cart = request.session.get('cart', [])
    
    if 0 <= index < len(cart):
        cart.pop(index)
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('cart_view')

def update_cart_quantity(request, index):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        quantity = int(request.POST.get('quantity', 1))
        
        if 0 <= index < len(cart) and quantity > 0:
            cart[index]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
    
    return redirect('cart_view')

def checkout(request):
    from decimal import Decimal
    from .models import Coupon
    
    cart = request.session.get('cart', [])
    total = Decimal(str(sum(float(item['price']) * item['quantity'] for item in cart)))
    coupon_discount = Decimal('0')
    coupon_code = request.session.get('coupon_code', '')
    
    if request.method == 'POST':
        # Check if removing coupon
        if 'remove_coupon' in request.POST:
            request.session['coupon_code'] = ''
            request.session['coupon_discount'] = 0
            request.session.modified = True
            
            return render(request, 'shop/checkout.html', {
                'cart': cart,
                'total': total,
                'success': '✅ Coupon removed successfully!'
            })
        
        # Check if applying coupon
        elif 'apply_coupon' in request.POST:
            coupon_code = request.POST.get('coupon_code', '').strip().upper()
            
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                
                if not coupon.is_valid():
                    return render(request, 'shop/checkout.html', {
                        'cart': cart,
                        'total': total,
                        'error': '❌ This coupon is no longer valid or has expired!'
                    })
                
                coupon_discount = Decimal(str(coupon.get_discount_amount(total)))
                request.session['coupon_code'] = coupon_code
                request.session['coupon_discount'] = float(coupon_discount)
                request.session.modified = True
                
                return render(request, 'shop/checkout.html', {
                    'cart': cart,
                    'total': total,
                    'coupon_code': coupon_code,
                    'coupon_discount': coupon_discount,
                    'final_total': total - coupon_discount,
                    'success': f'✅ Coupon "{coupon_code}" applied successfully!'
                })
            
            except Coupon.DoesNotExist:
                return render(request, 'shop/checkout.html', {
                    'cart': cart,
                    'total': total,
                    'error': '❌ Invalid coupon code!'
                })
        
        # Place order
        else:
            coupon_discount = Decimal(str(request.session.get('coupon_discount', 0)))
            final_total = total - coupon_discount
            
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=request.POST.get('name'),
                customer_email=request.POST.get('email'),
                customer_phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                postal_code=request.POST.get('postal_code'),
                total_amount=final_total
            )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['product_name'],
                    variant_text=item['variant_text'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Increment coupon usage
            if coupon_code:
                coupon = Coupon.objects.get(code=coupon_code)
                coupon.times_used += 1
                coupon.save()
            
            # Clear cart and coupon
            request.session['cart'] = []
            request.session['coupon_code'] = ''
            request.session['coupon_discount'] = 0
            request.session.modified = True
            
            return redirect('order_confirmation', order_id=order.id)
    
    # Get coupon info if already applied
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                coupon_discount = Decimal(str(coupon.get_discount_amount(total)))
        except Coupon.DoesNotExist:
            pass
    
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'total': total,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'final_total': total - coupon_discount,
    })


def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()
    
    return render(request, 'shop/order_confirmation.html', {
        'order': order,
        'items': items
    })

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check if passwords match
        if password != password2:
            return render(request, 'shop/signup.html', {'error': 'Passwords do not match!'})
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'shop/signup.html', {'error': 'Username already taken!'})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'shop/signup.html', {'error': 'Email already registered!'})
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Auto-login after signup
        login(request, user)
        return redirect('home')
    
    return render(request, 'shop/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials!'})
    
    return render(request, 'shop/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login_view')
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'shop/profile.html', {
        'user': user,
        'orders': orders
    })

@login_required(login_url='login_view')
def add_review(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        from .models import Review
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
        
        return redirect('product_detail', id=product_id)
    
    return redirect('product_detail', id=product_id)
