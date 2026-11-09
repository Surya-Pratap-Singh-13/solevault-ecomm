from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_svg = models.TextField(blank=True, help_text="SVG code or icon name for category")
    image_url = models.URLField(max_length=500, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    material = models.CharField(max_length=100, default="Breathable Mesh & Cushioned EVA")
    color = models.CharField(max_length=80, default="Midnight Black / Cyber Red")
    image_url = models.URLField(max_length=600)
    additional_images = models.TextField(
        blank=True,
        help_text="Comma-separated image URLs for product gallery"
    )
    stock = models.PositiveIntegerField(default=50)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    reviews_count = models.PositiveIntegerField(default=128)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > self.discount_price:
            pct = ((self.price - self.discount_price) / self.price) * 100
            return int(round(pct))
        return 0

    @property
    def gallery_images(self):
        urls = [self.image_url]
        if self.additional_images:
            for u in self.additional_images.split(','):
                u = u.strip()
                if u and u not in urls:
                    urls.append(u)
        return urls

    def __str__(self):
        return f"{self.brand} - {self.title}"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10)  # e.g. "US 7", "US 8", "US 9"
    stock = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'size')
        ordering = ['size']

    def __str__(self):
        return f"{self.product.title} - Size {self.size}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        total = sum(item.subtotal for item in self.items.all())
        return total

    @property
    def shipping_cost(self):
        if self.subtotal == 0 or self.subtotal >= 100:
            return Decimal('0.00')
        return Decimal('9.99')

    @property
    def tax(self):
        return (self.subtotal * Decimal('0.08')).quantize(Decimal('0.01'))

    @property
    def grand_total(self):
        return self.subtotal + self.shipping_cost + self.tax

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} (User: {self.user or self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=15, default="US 9")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.title} ({self.size})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Order Confirmed'),
        ('PACKED', 'Packed & Quality Checked'),
        ('SHIPPED', 'In Transit / Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('CARD', 'Credit / Debit Card'),
        ('UPI', 'Instant UPI / QR'),
        ('NET_BANKING', 'Net Banking'),
        ('COD', 'Cash on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid Successfully'),
        ('PENDING', 'Payment Pending'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Customer Details
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    
    # Shipping Address
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Info
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='CARD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Tracking & Fulfillment Info
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='CONFIRMED')
    tracking_number = models.CharField(max_length=80, unique=True)
    courier_name = models.CharField(max_length=100, default='SwiftAir Global Logistics')
    estimated_delivery = models.CharField(max_length=100, default='3 - 5 Business Days')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.full_name}"

    @property
    def progress_percentage(self):
        steps = {
            'PLACED': 15,
            'CONFIRMED': 35,
            'PACKED': 55,
            'SHIPPED': 75,
            'OUT_FOR_DELIVERY': 90,
            'DELIVERED': 100,
            'CANCELLED': 0
        }
        return steps.get(self.status, 20)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_title = models.CharField(max_length=200)
    product_brand = models.CharField(max_length=100)
    product_image = models.URLField(max_length=600)
    size = models.CharField(max_length=15)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_title} in Order #{self.order.order_number}"


class TrackingEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_events')
    status_title = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.status_title}"
