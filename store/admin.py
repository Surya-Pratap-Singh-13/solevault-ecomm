from django.contrib import admin
from .models import Category, Product, ProductSize, Cart, CartItem, Order, OrderItem, TrackingEvent


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'price', 'discount_price', 'stock', 'is_featured', 'is_trending')
    list_filter = ('category', 'brand', 'is_featured', 'is_trending')
    search_fields = ('title', 'brand', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductSizeInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'product_brand', 'size', 'price', 'quantity', 'subtotal')


class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'total_amount', 'status', 'payment_status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'full_name', 'email', 'tracking_number')
    inlines = [OrderItemInline, TrackingEventInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at', 'updated_at')


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('order', 'status_title', 'location', 'timestamp')
