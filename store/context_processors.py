from .models import Cart

def cart_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.item_count
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
            if cart:
                cart_count = cart.item_count
    return {
        'nav_cart_count': cart_count,
        'current_user': request.user if request.user.is_authenticated else None,
    }
