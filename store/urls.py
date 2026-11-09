from django.urls import path
from . import views

urlpatterns = [
    # Catalog & Shopping
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    
    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/process/', views.process_payment, name='process_payment'),
    
    # Tracking & Buyer Orders
    path('orders/track/<str:order_number>/', views.order_tracking, name='order_tracking'),
    path('orders/track/<str:order_number>/simulate-progress/', views.simulate_tracking_progress, name='simulate_tracking_progress'),
    path('orders/', views.order_history, name='order_history'),

    # Authentication
    path('auth/register/', views.user_register, name='register'),
    path('auth/login/', views.user_login, name='login'),
    path('auth/logout/', views.user_logout, name='logout'),
]
