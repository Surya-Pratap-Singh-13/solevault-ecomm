"""
Database Seeding Module for SoleVault E-Commerce Store.
Populates realistic demo users, shoe categories, products, size stock,
active buyer cart, and lifecycle orders with tracking history.
"""

from decimal import Decimal
from django.contrib.auth.models import User
from store.models import Category, Product, ProductSize, Cart, CartItem, Order, OrderItem, TrackingEvent


def seed_database(reset=False, log=None):
    """
    Seed the database with comprehensive demo data.
    If reset=True, removes previous demo records before inserting.
    `log` can be a custom print function or command.stdout.write.
    """
    if log is None:
        log = print

    if reset:
        log("🧹 Resetting existing demo data...")
        TrackingEvent.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        ProductSize.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(username__in=['admin', 'buyer', 'sarah']).delete()
        log("✓ Cleaned previous demo data.")

    log("🌱 Starting demo database seeding...")

    # ==========================================
    # 1. Demo Users
    # ==========================================
    # Superuser Admin
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@shoestore.com',
            password='admin123'
        )
        admin_user.first_name = 'Store'
        admin_user.last_name = 'Admin'
        admin_user.save()
        log("  ✓ Created Superuser: admin / admin123")
    else:
        admin_user.set_password('admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        log("  ✓ Verified Superuser: admin / admin123")

    # Primary Demo Buyer
    demo_buyer, buyer_created = User.objects.get_or_create(
        username='buyer',
        defaults={
            'email': 'buyer@example.com',
            'first_name': 'Alex',
            'last_name': 'Mercer',
        }
    )
    demo_buyer.set_password('password123')
    demo_buyer.first_name = 'Alex'
    demo_buyer.last_name = 'Mercer'
    demo_buyer.email = 'buyer@example.com'
    demo_buyer.save()
    log("  ✓ Created/Updated Demo Buyer: buyer / password123")

    # Secondary Demo Buyer
    sarah_buyer, sarah_created = User.objects.get_or_create(
        username='sarah',
        defaults={
            'email': 'sarah@example.com',
            'first_name': 'Sarah',
            'last_name': 'Connor',
        }
    )
    sarah_buyer.set_password('password123')
    sarah_buyer.first_name = 'Sarah'
    sarah_buyer.last_name = 'Connor'
    sarah_buyer.email = 'sarah@example.com'
    sarah_buyer.save()
    log("  ✓ Created/Updated Demo Buyer: sarah / password123")

    # ==========================================
    # 2. Categories
    # ==========================================
    categories_data = [
        {
            'name': 'Running Shoes',
            'slug': 'running',
            'description': 'High-rebound marathon runners, trail trainers, and ultralight sprinting footwear.',
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80',
        },
        {
            'name': 'Sneakers & Streetwear',
            'slug': 'sneakers',
            'description': 'Iconic silhouettes, retro high-tops, and modern aesthetic street kicks.',
            'image_url': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600&auto=format&fit=crop&q=80',
        },
        {
            'name': 'Sports & Basketball',
            'slug': 'sports',
            'description': 'Ankle-stabilizing court footwear with maximum spring and traction grip.',
            'image_url': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=600&auto=format&fit=crop&q=80',
        },
        {
            'name': 'Casual & Loafers',
            'slug': 'casual',
            'description': 'Everyday slip-ons, minimalist tennis shoes, and versatile suede silhouettes.',
            'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600&auto=format&fit=crop&q=80',
        },
        {
            'name': 'Outdoor & Hiking Boots',
            'slug': 'boots',
            'description': 'Waterproof Vibram tread boots engineered for rugged trails and mountain terrain.',
            'image_url': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80',
        },
        {
            'name': 'Training & Gym',
            'slug': 'training',
            'description': 'Cross-training stability shoes, flat-sole lifting trainers, and HIIT workout gear.',
            'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80',
        },
    ]

    cat_map = {}
    for cdata in categories_data:
        cat, _ = Category.objects.update_or_create(
            slug=cdata['slug'],
            defaults={
                'name': cdata['name'],
                'description': cdata['description'],
                'image_url': cdata['image_url'],
            }
        )
        cat_map[cdata['slug']] = cat
    log(f"  ✓ Seeded {len(cat_map)} footwear categories.")

    # ==========================================
    # 3. Products
    # ==========================================
    products_data = [
        {
            'title': 'Air VaporMax Flyknit Blaze',
            'slug': 'air-vapormax-flyknit-blaze',
            'category': cat_map['running'],
            'brand': 'Nike',
            'price': Decimal('210.00'),
            'discount_price': Decimal('175.00'),
            'short_description': 'Ultra-responsive air pod cushioning with featherlight recycled Flyknit upper.',
            'description': 'Built for endless energy return, the Air VaporMax Flyknit Blaze replaces traditional foam with revolutionary standalone Air pods. Engineered with seamless Flyknit yarn, this silhouette delivers sock-like snugness, elite breathability, and instant propulsion whether tackling marathon asphalt or downtown streets.',
            'material': 'Flyknit Textile & Recycled TPU Air Unit',
            'color': 'Crimson Velocity / Obsidian Black',
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80,https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop&q=80',
            'stock': 45,
            'rating': Decimal('4.9'),
            'reviews_count': 342,
            'is_featured': True,
            'is_trending': True,
        },
        {
            'title': 'Ultraboost 24 Solar Boost',
            'slug': 'ultraboost-24-solar-boost',
            'category': cat_map['running'],
            'brand': 'Adidas',
            'price': Decimal('190.00'),
            'discount_price': Decimal('159.99'),
            'short_description': 'Maximum energy return with Linear Energy Push torsion and Primeknit+ mesh.',
            'description': 'Experience peerless kinetic propulsion with the Ultraboost 24 Solar Boost. Packing 20% more microscopic energy capsules into the Light BOOST midsole, every footstrike yields explosive rebound. Reinforced with Continental Rubber grip for wet and dry pavement stability.',
            'material': 'Primeknit+ Upper & Light BOOST Midsole',
            'color': 'Solar White / Core Black',
            'image_url': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80,https://images.unsplash.com/photo-1556906781-9a412961c28c?w=800&auto=format&fit=crop&q=80',
            'stock': 60,
            'rating': Decimal('4.8'),
            'reviews_count': 210,
            'is_featured': True,
            'is_trending': False,
        },
        {
            'title': 'Retro High Chicago OG',
            'slug': 'retro-high-chicago-og',
            'category': cat_map['sneakers'],
            'brand': 'Jordan',
            'price': Decimal('225.00'),
            'discount_price': Decimal('199.00'),
            'short_description': 'Timeless 1985 basketball court DNA crafted in full-grain premium leather.',
            'description': 'The sneaker that revolutionized court culture and streetwear forever. The Retro High Chicago OG pairs vintage color-blocking with supple genuine tumbled leather. Complete with encapsulated Air-Sole cushioning in the heel and durable pivot-circle traction outsole.',
            'material': 'Full-Grain Tumbled Leather & Solid Rubber Cupsole',
            'color': 'Varsity Red / Summit White / Black',
            'image_url': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80,https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=800&auto=format&fit=crop&q=80',
            'stock': 28,
            'rating': Decimal('5.0'),
            'reviews_count': 512,
            'is_featured': True,
            'is_trending': True,
        },
        {
            'title': 'NB 550 Vintage Green Court',
            'slug': 'nb-550-vintage-green-court',
            'category': cat_map['sneakers'],
            'brand': 'New Balance',
            'price': Decimal('130.00'),
            'discount_price': Decimal('115.00'),
            'short_description': 'Clean retro court aesthetic with streamlined leather and perforated accents.',
            'description': 'A tribute to 1989 basketball heritage, the 550 delivers effortless retro street aesthetics. Crafted from premium leather with perforated side panels and vintage pine green accents. Perfect for all-day campus walking, cafe hangs, and relaxed weekend styling.',
            'material': 'Smooth Perforated Leather & Suede Mudguard',
            'color': 'Sea Salt / Pine Green / Cream',
            'image_url': 'https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1539185441755-769473a23570?w=800&auto=format&fit=crop&q=80',
            'stock': 35,
            'rating': Decimal('4.7'),
            'reviews_count': 189,
            'is_featured': False,
            'is_trending': True,
        },
        {
            'title': 'Precision Court Pro High',
            'slug': 'precision-court-pro-high',
            'category': cat_map['sports'],
            'brand': 'Puma',
            'price': Decimal('145.00'),
            'discount_price': Decimal('120.00'),
            'short_description': 'Explosive high-top basketball shoes with dual-density ProFoam cushioning.',
            'description': 'Dominate both paint and perimeter. Precision Court Pro High provides reinforced ankle lockdown collars, dual-density ProFoam response, and high-abrasion non-marking sticky rubber for rapid cross-court directional cuts.',
            'material': 'Engineered Ripstop Mesh & Synthetic Suede',
            'color': 'Neon Lime / Stealth Grey / Black',
            'image_url': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=800&auto=format&fit=crop&q=80',
            'stock': 40,
            'rating': Decimal('4.6'),
            'reviews_count': 94,
            'is_featured': False,
            'is_trending': False,
        },
        {
            'title': 'Gel-Kayano 30 Stability',
            'slug': 'gel-kayano-30-stability',
            'category': cat_map['running'],
            'brand': 'Asics',
            'price': Decimal('170.00'),
            'discount_price': Decimal('149.00'),
            'short_description': '4D Guidance System providing adaptive stability and pure foot comfort.',
            'description': 'From 5Ks to full marathons, the Gel-Kayano 30 is the benchmark of structured stability. The revolutionary 4D GUIDANCE SYSTEM adapts to your stride cadence, while PureGEL technology delivers cloud-soft heel transitions.',
            'material': 'Engineered Stretch Knit & FF BLAST PLUS Foam',
            'color': 'Monaco Blue / Electric Lime',
            'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&auto=format&fit=crop&q=80',
            'stock': 55,
            'rating': Decimal('4.9'),
            'reviews_count': 267,
            'is_featured': False,
            'is_trending': True,
        },
        {
            'title': 'Chelsea Urban Suede Loafer',
            'slug': 'chelsea-urban-suede-loafer',
            'category': cat_map['casual'],
            'brand': 'SoleVault Signature',
            'price': Decimal('160.00'),
            'discount_price': Decimal('135.00'),
            'short_description': 'Hand-stitched Italian suede loafers with orthopedic memory foam insole.',
            'description': 'Bridging formal elegance and weekend comfort, the Chelsea Urban Suede Loafer features velvety Italian calf suede, elasticated side gussets, and a shock-absorbing crepe rubber sole designed for effortless day-to-night transitions.',
            'material': '100% Italian Calf Suede & Natural Crepe Sole',
            'color': 'Desert Camel / Tobacco Brown',
            'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80',
            'stock': 22,
            'rating': Decimal('4.8'),
            'reviews_count': 82,
            'is_featured': True,
            'is_trending': False,
        },
        {
            'title': 'Apex Trail Waterproof Boot',
            'slug': 'apex-trail-waterproof-boot',
            'category': cat_map['boots'],
            'brand': 'Columbia',
            'price': Decimal('185.00'),
            'discount_price': Decimal('159.00'),
            'short_description': 'Seam-sealed Gore-Tex membrane hiking boot with multidirectional traction.',
            'description': 'Tackle rain, mud, and mountain passes with unwavering confidence. The Apex Trail Boot combines rugged waterproof leather with a breathable internal membrane, padded collar, and Vibram Megagrip lug outsole for impenetrable mountain durability.',
            'material': 'Waterproof Nubuck Leather & Gore-Tex Tech',
            'color': 'Earthy Olive / Rust Bronze',
            'image_url': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800&auto=format&fit=crop&q=80',
            'stock': 30,
            'rating': Decimal('4.9'),
            'reviews_count': 148,
            'is_featured': False,
            'is_trending': True,
        },
        {
            'title': 'Air Force 1 07 Low Clean White',
            'slug': 'air-force-1-07-low-clean-white',
            'category': cat_map['sneakers'],
            'brand': 'Nike',
            'price': Decimal('115.00'),
            'discount_price': None,
            'short_description': 'The pristine icon of street fashion, crisp stitched leather and Air comfort.',
            'description': 'The radiance lives on in the Nike Air Force 1 07, the b-ball icon that puts a fresh spin on what you know best: crisp leather, bold details and the perfect amount of flash to make you shine.',
            'material': 'Full-Grain White Leather & Nike Air Cushioning',
            'color': 'Triple White',
            'image_url': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=800&auto=format&fit=crop&q=80',
            'stock': 50,
            'rating': Decimal('4.9'),
            'reviews_count': 640,
            'is_featured': True,
            'is_trending': True,
        },
        {
            'title': 'Speedcross 6 Trail Gripper',
            'slug': 'speedcross-6-trail-gripper',
            'category': cat_map['training'],
            'brand': 'Salomon',
            'price': Decimal('155.00'),
            'discount_price': Decimal('139.00'),
            'short_description': 'Aggressive chevron lug geometry with Quicklace system for muddy technical trails.',
            'description': 'Salomon Speedcross 6 stays true to its legendary trail roots. Lighter than ever with an upgraded Mud Contagrip sole that sheds mud quicker and adheres fiercely to wet rocks and steep inclines.',
            'material': 'Anti-Debris Mesh & Contagrip Rubber Compound',
            'color': 'Acid Mint / Deep Ink / Black',
            'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80',
            'stock': 32,
            'rating': Decimal('4.8'),
            'reviews_count': 112,
            'is_featured': False,
            'is_trending': True,
        },
        {
            'title': 'Heritage 6-Inch Premium Boot',
            'slug': 'heritage-6-inch-premium-boot',
            'category': cat_map['boots'],
            'brand': 'Timberland',
            'price': Decimal('210.00'),
            'discount_price': Decimal('189.00'),
            'short_description': 'Waterproof seam-sealed wheat nubuck leather with PrimaLoft insulation.',
            'description': 'The original yellow waterproof boot that started it all. Featuring 400 grams of warm PrimaLoft insulation, anti-fatigue removable footbeds, rustproof hardware, and rubber lug outsoles that withstand snow, sleet, and urban exploration.',
            'material': 'Premium Waterproof Wheat Nubuck & Anti-Fatigue Foam',
            'color': 'Wheat Yellow / Gold / Rust',
            'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
            'stock': 25,
            'rating': Decimal('4.9'),
            'reviews_count': 380,
            'is_featured': True,
            'is_trending': False,
        },
        {
            'title': 'Old Skool Core Skate Classic',
            'slug': 'old-skool-core-skate-classic',
            'category': cat_map['sneakers'],
            'brand': 'Vans',
            'price': Decimal('80.00'),
            'discount_price': Decimal('69.99'),
            'short_description': 'Iconic sidestripe silhouette with reinforced toecaps and signature waffle sole.',
            'description': 'First known as the Vans #36, the Old Skool debuted in 1977 with a unique new addition: a random doodle drawn by founder Paul Van Doren, originally referred to as the "jazz stripe." Today, the famed Vans Sidestripe has become the unmistakable hallmark of the brand.',
            'material': 'Sturdy Canvas, Suede Uppers & Rubber Waffle Outsole',
            'color': 'Black / True White',
            'image_url': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&auto=format&fit=crop&q=80',
            'additional_images': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&auto=format&fit=crop&q=80',
            'stock': 65,
            'rating': Decimal('4.7'),
            'reviews_count': 420,
            'is_featured': False,
            'is_trending': False,
        },
    ]

    sizes_list = ['US 7', 'US 7.5', 'US 8', 'US 8.5', 'US 9', 'US 9.5', 'US 10', 'US 10.5', 'US 11', 'US 12']

    created_prods = []
    for pdata in products_data:
        prod, _ = Product.objects.update_or_create(
            slug=pdata['slug'],
            defaults=pdata
        )
        created_prods.append(prod)

        for s in sizes_list:
            ProductSize.objects.get_or_create(
                product=prod,
                size=s,
                defaults={'stock': 15}
            )

    log(f"  ✓ Seeded {len(created_prods)} shoe models with {len(sizes_list)} size options each.")

    # ==========================================
    # 4. Demo Buyer Shopping Cart
    # ==========================================
    buyer_cart, _ = Cart.objects.get_or_create(user=demo_buyer)
    buyer_cart.items.all().delete()

    cart_prod_1 = Product.objects.filter(slug='ultraboost-24-solar-boost').first() or created_prods[0]
    cart_prod_2 = Product.objects.filter(slug='retro-high-chicago-og').first() or created_prods[1]

    CartItem.objects.create(
        cart=buyer_cart,
        product=cart_prod_1,
        size='US 9.5',
        quantity=1
    )
    CartItem.objects.create(
        cart=buyer_cart,
        product=cart_prod_2,
        size='US 10',
        quantity=1
    )
    log(f"  ✓ Pre-populated active cart with 2 items for buyer ({demo_buyer.username}).")

    # ==========================================
    # 5. Orders & Live Tracking Events for Demo Buyer
    # ==========================================
    # Order 1: In Transit / SHIPPED (can be advanced with simulation button!)
    order1_num = 'SHOE-2026-892147'
    p1 = Product.objects.filter(slug='air-vapormax-flyknit-blaze').first() or created_prods[0]
    p2 = Product.objects.filter(slug='nb-550-vintage-green-court').first() or created_prods[3]

    subtotal1 = p1.current_price + p2.current_price
    tax1 = (subtotal1 * Decimal('0.08')).quantize(Decimal('0.01'))
    shipping1 = Decimal('0.00')  # Free shipping over $100
    total1 = subtotal1 + tax1 + shipping1

    order1, _ = Order.objects.update_or_create(
        order_number=order1_num,
        defaults={
            'user': demo_buyer,
            'full_name': 'Alex Mercer',
            'email': 'buyer@example.com',
            'phone': '+1 (555) 782-9901',
            'address': '742 Evergreen Terrace',
            'city': 'Springfield',
            'state': 'Oregon',
            'postal_code': '97477',
            'country': 'United States',
            'subtotal': subtotal1,
            'shipping_cost': shipping1,
            'tax': tax1,
            'total_amount': total1,
            'payment_method': 'CARD',
            'payment_status': 'PAID',
            'transaction_id': 'TXN-A8F923D48102',
            'status': 'SHIPPED',
            'tracking_number': 'TRK-EXP-98218734',
            'courier_name': 'SwiftAir Express Logistics',
            'estimated_delivery': 'Tomorrow by 7:00 PM',
        }
    )

    # Order 1 items
    order1.items.all().delete()
    OrderItem.objects.create(
        order=order1,
        product=p1,
        product_title=p1.title,
        product_brand=p1.brand,
        product_image=p1.image_url,
        size='US 9',
        price=p1.current_price,
        quantity=1,
        subtotal=p1.current_price,
    )
    OrderItem.objects.create(
        order=order1,
        product=p2,
        product_title=p2.title,
        product_brand=p2.brand,
        product_image=p2.image_url,
        size='US 9.5',
        price=p2.current_price,
        quantity=1,
        subtotal=p2.current_price,
    )

    # Order 1 tracking events
    order1.tracking_events.all().delete()
    TrackingEvent.objects.create(
        order=order1,
        status_title='Order Placed & Payment Verified',
        location='Online Secure Checkout (Txn Verified)',
        message='Payment confirmed via Credit Card. Order received and sent to regional fulfillment station.',
        is_completed=True
    )
    TrackingEvent.objects.create(
        order=order1,
        status_title='Quality Check Passed & Packed',
        location='SoleVault Fulfillment Center Hub A, Oregon',
        message='12-point sneaker authenticity verified. Package boxed with anti-tamper security seal.',
        is_completed=True
    )
    TrackingEvent.objects.create(
        order=order1,
        status_title='In Transit - Air Freight Departure',
        location='Regional Linehaul Terminal, Portland OR',
        message='Package loaded into flight SAF-924. En route to local destination delivery hub.',
        is_completed=True
    )

    # Order 2: Fully DELIVERED
    order2_num = 'SHOE-2026-773410'
    p3 = Product.objects.filter(slug='retro-high-chicago-og').first() or created_prods[2]
    subtotal2 = p3.current_price
    tax2 = (subtotal2 * Decimal('0.08')).quantize(Decimal('0.01'))
    shipping2 = Decimal('0.00')
    total2 = subtotal2 + tax2 + shipping2

    order2, _ = Order.objects.update_or_create(
        order_number=order2_num,
        defaults={
            'user': demo_buyer,
            'full_name': 'Alex Mercer',
            'email': 'buyer@example.com',
            'phone': '+1 (555) 782-9901',
            'address': '742 Evergreen Terrace',
            'city': 'Springfield',
            'state': 'Oregon',
            'postal_code': '97477',
            'country': 'United States',
            'subtotal': subtotal2,
            'shipping_cost': shipping2,
            'tax': tax2,
            'total_amount': total2,
            'payment_method': 'UPI',
            'payment_status': 'PAID',
            'transaction_id': 'TXN-U77821946001',
            'status': 'DELIVERED',
            'tracking_number': 'TRK-EXP-44129081',
            'courier_name': 'SwiftAir Express Logistics',
            'estimated_delivery': 'Delivered on Monday',
        }
    )
    order2.items.all().delete()
    OrderItem.objects.create(
        order=order2,
        product=p3,
        product_title=p3.title,
        product_brand=p3.brand,
        product_image=p3.image_url,
        size='US 10',
        price=p3.current_price,
        quantity=1,
        subtotal=p3.current_price,
    )
    order2.tracking_events.all().delete()
    for t_title, t_loc, t_msg in [
        ('Order Placed & Payment Verified', 'Online Secure Checkout', 'Instant UPI payment received. Order forwarded to warehouse.'),
        ('Packed & Authenticity Sealed', 'SoleVault Warehouse Hub B', 'Authenticity badge attached. Box packaged in eco-cushion pack.'),
        ('In Transit Across States', 'Interstate Distribution Hub, Nevada', 'Shipment scanned and forwarded to regional postal sort facility.'),
        ('Out for Delivery', 'Local Delivery Center, Springfield OR', 'Courier driver Mark has loaded the parcel onto the van.'),
        ('Package Delivered & Signed', '742 Evergreen Terrace, Springfield', 'Delivered safely to front porch / resident. Enjoy your kicks!'),
    ]:
        TrackingEvent.objects.create(
            order=order2,
            status_title=t_title,
            location=t_loc,
            message=t_msg,
            is_completed=True
        )

    # Order 3: PACKED / Processing
    order3_num = 'SHOE-2026-551092'
    p4 = Product.objects.filter(slug='chelsea-urban-suede-loafer').first() or created_prods[4]
    subtotal3 = p4.current_price
    tax3 = (subtotal3 * Decimal('0.08')).quantize(Decimal('0.01'))
    shipping3 = Decimal('0.00')
    total3 = subtotal3 + tax3 + shipping3

    order3, _ = Order.objects.update_or_create(
        order_number=order3_num,
        defaults={
            'user': demo_buyer,
            'full_name': 'Alex Mercer',
            'email': 'buyer@example.com',
            'phone': '+1 (555) 782-9901',
            'address': '742 Evergreen Terrace',
            'city': 'Springfield',
            'state': 'Oregon',
            'postal_code': '97477',
            'country': 'United States',
            'subtotal': subtotal3,
            'shipping_cost': shipping3,
            'tax': tax3,
            'total_amount': total3,
            'payment_method': 'NET_BANKING',
            'payment_status': 'PAID',
            'transaction_id': 'TXN-NB-33491820',
            'status': 'PACKED',
            'tracking_number': 'TRK-EXP-11098453',
            'courier_name': 'SwiftAir Express Logistics',
            'estimated_delivery': 'In 3 Business Days',
        }
    )
    order3.items.all().delete()
    OrderItem.objects.create(
        order=order3,
        product=p4,
        product_title=p4.title,
        product_brand=p4.brand,
        product_image=p4.image_url,
        size='US 8.5',
        price=p4.current_price,
        quantity=1,
        subtotal=p4.current_price,
    )
    order3.tracking_events.all().delete()
    for t_title, t_loc, t_msg in [
        ('Order Placed & Verified', 'Online Secure Checkout', 'Net Banking transaction authorized.'),
        ('Packed & Awaiting Carrier', 'SoleVault Central Depot', 'Inspected, boxed, and waiting for courier dispatch truck.'),
    ]:
        TrackingEvent.objects.create(
            order=order3,
            status_title=t_title,
            location=t_loc,
            message=t_msg,
            is_completed=True
        )

    log(f"  ✓ Seeded {Order.objects.filter(user=demo_buyer).count()} demo orders with full tracking lifecycles for buyer.")

    log("\n==========================================")
    log("🎉 Demo Seeding Completed Successfully!")
    log("==========================================")
    log(f"Users:        {User.objects.count()} (admin: 'admin' / 'admin123', buyer: 'buyer' / 'password123')")
    log(f"Categories:   {Category.objects.count()}")
    log(f"Products:     {Product.objects.count()}")
    log(f"ProductSizes: {ProductSize.objects.count()}")
    log(f"Orders:       {Order.objects.count()}")
    log(f"Cart Items:   {buyer_cart.items.count()} (in demo buyer's cart)")
    log("==========================================\n")
