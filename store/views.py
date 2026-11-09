from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
import uuid
import random

from .models import Category, Product, ProductSize, Cart, CartItem, Order, OrderItem, TrackingEvent


def _get_or_create_cart(request):
    """Retrieve existing cart or create a new one based on user or session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # If there's an anonymous cart in session, merge it
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    existing = cart.items.filter(product=item.product, size=item.size).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def home(request):
    """Buyer's Home Page: Browse shoe categories, featured drops, filter & search."""
    categories = Category.objects.all()
    products = Product.objects.all()

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category filter
    selected_category_slug = request.GET.get('category', '')
    selected_category = None
    if selected_category_slug:
        selected_category = get_object_or_404(Category, slug=selected_category_slug)
        products = products.filter(category=selected_category)

    # Brand filter
    selected_brand = request.GET.get('brand', '')
    if selected_brand:
        products = products.filter(brand__iexact=selected_brand)

    # Sorting
    sort_by = request.GET.get('sort', 'popular')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    # Distinct brands for filter sidebar / pill badges
    brands = Product.objects.values_list('brand', flat=True).distinct()
    featured_products = Product.objects.filter(is_featured=True)[:4]

    context = {
        'categories': categories,
        'products': products,
        'featured_products': featured_products,
        'selected_category': selected_category,
        'selected_category_slug': selected_category_slug,
        'selected_brand': selected_brand,
        'brands': brands,
        'query': query,
        'sort_by': sort_by,
        'total_products': products.count(),
    }
    return render(request, 'store/home.html', context)


def product_detail(request, slug):
    """Product Detail Page: View shoe specs, gallery, sizes, reviews and add to cart."""
    product = get_object_or_404(Product, slug=slug)
    sizes = product.sizes.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'sizes': sizes,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Add selected shoe with size to the buyer's cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)
    
    size = request.POST.get('size', 'US 9')
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Check for AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
        return JsonResponse({
            'success': True,
            'message': f"{product.title} (Size {size}) added to your cart!",
            'cart_count': cart.item_count,
            'subtotal': str(cart.subtotal),
        })

    messages.success(request, f"Added {product.title} (Size {size}) to your cart.")
    return redirect('cart')


def cart_view(request):
    """Buyer's Cart Page: Review items, update quantities, see bill summary."""
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    # Free shipping threshold is $100
    free_shipping_threshold = 100
    subtotal_num = float(cart.subtotal)
    amount_needed_for_free_shipping = max(0.0, free_shipping_threshold - subtotal_num)
    shipping_progress = min(100, int((subtotal_num / free_shipping_threshold) * 100)) if free_shipping_threshold else 100

    context = {
        'cart': cart,
        'items': items,
        'amount_needed_for_free_shipping': f"{amount_needed_for_free_shipping:.2f}",
        'shipping_progress': shipping_progress,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Update item quantity or delete item in cart."""
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    action = request.POST.get('action')
    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_quantity': item.quantity if item.id else 0,
            'item_subtotal': str(item.subtotal) if item.id else "0.00",
            'cart_subtotal': str(cart.subtotal),
            'cart_tax': str(cart.tax),
            'cart_shipping': str(cart.shipping_cost),
            'cart_grand_total': str(cart.grand_total),
            'cart_count': cart.item_count,
        })

    return redirect('cart')


@login_required
def checkout_view(request):
    """Payment & Shipping Details Page: Enter delivery address & select payment method."""
    cart = _get_or_create_cart(request)
    if cart.item_count == 0:
        messages.warning(request, "Your cart is currently empty. Pick some shoes first!")
        return redirect('home')

    items = cart.items.select_related('product').all()
    user = request.user

    initial_data = {
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'email': user.email or f"{user.username}@example.com",
    }

    context = {
        'cart': cart,
        'items': items,
        'initial_data': initial_data,
    }
    return render(request, 'store/checkout.html', context)


@login_required
@require_POST
def process_payment(request):
    """Process simulated payment, record the order, create tracking details, and respond."""
    cart = _get_or_create_cart(request)
    if cart.item_count == 0:
        return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)

    # Collect form data
    full_name = request.POST.get('full_name', '').strip() or request.user.username
    email = request.POST.get('email', '').strip() or request.user.email or "buyer@shoestore.com"
    phone = request.POST.get('phone', '').strip() or "+1 (555) 382-9901"
    address = request.POST.get('address', '').strip() or "742 Evergreen Terrace"
    city = request.POST.get('city', '').strip() or "Springfield"
    state = request.POST.get('state', '').strip() or "Oregon"
    postal_code = request.POST.get('postal_code', '').strip() or "97477"
    country = request.POST.get('country', '').strip() or "United States"
    payment_method = request.POST.get('payment_method', 'CARD')

    # Generate random unique Order Number & Tracking Number
    random_digits = random.randint(100000, 999999)
    order_number = f"SHOE-2026-{random_digits}"
    tracking_number = f"TRK-{random.choice(['EXP', 'AIR', 'FED'])}-{random.randint(10000000, 99999999)}"
    transaction_id = f"TXN-{(uuid.uuid4().hex[:12]).upper()}"

    # Create Order
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        subtotal=cart.subtotal,
        shipping_cost=cart.shipping_cost,
        tax=cart.tax,
        total_amount=cart.grand_total,
        payment_method=payment_method,
        payment_status='PAID',
        transaction_id=transaction_id,
        status='CONFIRMED',
        tracking_number=tracking_number,
        courier_name='SwiftAir Express Logistics',
        estimated_delivery='3 - 5 Business Days',
    )

    # Transfer cart items to order items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_title=item.product.title,
            product_brand=item.product.brand,
            product_image=item.product.image_url,
            size=item.size,
            price=item.product.current_price,
            quantity=item.quantity,
            subtotal=item.subtotal,
        )

    # Clear buyer's cart
    cart.items.all().delete()

    # Initial tracking milestones
    now = timezone.now()
    TrackingEvent.objects.create(
        order=order,
        status_title="Payment Verified & Order Received",
        location="Online Secure Gateway (Processed)",
        message=f"Payment authorized via {order.get_payment_method_display()} (Txn ID: {transaction_id}). Merchant has received and verified your order.",
        is_completed=True
    )
    TrackingEvent.objects.create(
        order=order,
        status_title="Order Packed & Quality Inspected",
        location="E-Commerce Central Warehouse, Hub A",
        message="Shoes have passed our 12-point authentication and quality checklist. Securely boxed and labeled for courier pickup.",
        is_completed=True
    )

    response_data = {
        'success': True,
        'order_number': order.order_number,
        'tracking_number': order.tracking_number,
        'total_amount': f"${order.total_amount:.2f}",
        'payment_method': order.get_payment_method_display(),
        'tracking_url': f"/orders/track/{order.order_number}/",
        'message': 'Payment completed successfully!',
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == 'true':
        return JsonResponse(response_data)

    messages.success(request, "Product Payment Complete! Track your order below.")
    return redirect('order_tracking', order_number=order.order_number)


@login_required
def order_tracking(request, order_number):
    """Live Tracking Page: View package timeline, courier status, map checkpoint, and update simulation."""
    order = get_object_or_404(Order, order_number=order_number)
    # Check authorization: user must own order unless staff
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to view this order's tracking details.")
        return redirect('home')

    tracking_events = order.tracking_events.all().order_by('id')

    # Status steps for the progress visualizer
    status_flow = [
        {'code': 'PLACED', 'title': 'Order Placed', 'icon': 'shopping-bag'},
        {'code': 'CONFIRMED', 'title': 'Confirmed', 'icon': 'check-circle'},
        {'code': 'PACKED', 'title': 'Packed', 'icon': 'box'},
        {'code': 'SHIPPED', 'title': 'In Transit', 'icon': 'truck'},
        {'code': 'OUT_FOR_DELIVERY', 'title': 'Out for Delivery', 'icon': 'map-pin'},
        {'code': 'DELIVERED', 'title': 'Delivered', 'icon': 'home'},
    ]

    status_keys = [s['code'] for s in status_flow]
    current_index = 0
    if order.status in status_keys:
        current_index = status_keys.index(order.status)
    elif order.status == 'CANCELLED':
        current_index = -1

    for idx, step in enumerate(status_flow):
        step['is_completed'] = idx <= current_index
        step['is_current'] = idx == current_index

    context = {
        'order': order,
        'tracking_events': tracking_events,
        'status_flow': status_flow,
        'current_status': order.status,
    }
    return render(request, 'store/order_tracking.html', context)


@login_required
@require_POST
def simulate_tracking_progress(request, order_number):
    """Demo feature: Progress the shipment to next milestone for real-time tracking demonstration."""
    order = get_object_or_404(Order, order_number=order_number)
    if order.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    transitions = {
        'PLACED': ('CONFIRMED', 'Order Confirmed', 'Merchant Fulfillment Center', 'Order accepted and confirmed by seller.'),
        'CONFIRMED': ('PACKED', 'Packed & Handed to Courier', 'Air Freight Hub', 'Package scanned and placed into linehaul vehicle.'),
        'PACKED': ('SHIPPED', 'In Transit Across Regional Facilities', 'Central Distribution Hub, Express Lane', 'En route to your local distribution center via SwiftAir flight.'),
        'SHIPPED': ('OUT_FOR_DELIVERY', 'Out for Delivery', f'Local Courier Station, {order.city}', f'Courier driver Alex is on the route to deliver your package to {order.address}.'),
        'OUT_FOR_DELIVERY': ('DELIVERED', 'Package Delivered & Signed', f'{order.address}, {order.city}', 'Successfully delivered directly to recipient. Thank you for shopping with us!'),
    }

    if order.status in transitions:
        next_status, title, loc, msg = transitions[order.status]
        order.status = next_status
        order.save()

        TrackingEvent.objects.create(
            order=order,
            status_title=title,
            location=loc,
            message=msg,
            is_completed=True
        )

        return JsonResponse({
            'success': True,
            'new_status': next_status,
            'status_display': order.get_status_display(),
            'message': f"Order updated to: {order.get_status_display()}"
        })

    return JsonResponse({'success': False, 'message': 'Order is already delivered or cannot be advanced further.'})


@login_required
def order_history(request):
    """Buyer's Order History: View all previous purchases with tracking links."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})


# Authentication Views
def user_register(request):
    """Buyer Registration view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'store/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'store/register.html', {
                'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'store/register.html', {
                'email': email, 'first_name': first_name, 'last_name': last_name
            })

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email is already associated with another account.")
            return render(request, 'store/register.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, f"Welcome to SoleVault, {user.first_name or user.username}! Happy shopping!")
        
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('home')

    return render(request, 'store/register.html')


def user_login(request):
    """Buyer Login view."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    next_url = request.GET.get('next', '')
    return render(request, 'store/login.html', {'next': next_url})


def user_logout(request):
    """Buyer Logout view."""
    logout(request)
    messages.info(request, "You have been logged out. See you next time!")
    return redirect('home')
