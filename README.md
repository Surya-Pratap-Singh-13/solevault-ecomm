# SoleVault - Premium Footwear E-Commerce

SoleVault is a modern Django-based sneaker and athletic footwear e-commerce application featuring product catalog filtering, cart management, seamless checkout, and real-time package delivery tracking simulation.

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Apply Migrations
```bash
python manage.py migrate
```

### 3. Run Demo Seeding
Populate the database with realistic demo categories, sneakers, users, active buyer carts, and tracked orders:

```bash
# Using Django management command
python manage.py seed_demo

# Or with reset flag to start fresh
python manage.py seed_demo --reset

# (Alias also supported)
python manage.py seed_data

# Or standalone script
python seed_data.py [--reset]
```

### 4. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Accounts

| Role | Username | Password | Notes |
|---|---|---|---|
| **Demo Buyer** | `buyer` | `password123` | Pre-loaded with 2 cart items & 3 orders across stages |
| **Second Buyer** | `sarah` | `password123` | Alternative buyer profile |
| **Superuser/Admin** | `admin` | `admin123` | Access to Django Admin at `/admin/` |

---

## 📦 What the Demo Seeding Includes

1. **User Accounts**:
   - `buyer` (Alex Mercer) with pre-filled address and sample purchase history.
   - `admin` superuser for the Django admin portal.
2. **6 Footwear Categories**:
   - Running Shoes, Sneakers & Streetwear, Sports & Basketball, Casual & Loafers, Outdoor & Hiking Boots, Training & Gym.
3. **12 Shoe Models**:
   - High-definition images, authentic brands (Nike, Adidas, Jordan, New Balance, Puma, Asics, Salomon, Timberland, Vans).
   - Realistic pricing, discounts, descriptions, colors, materials, and rating reviews.
4. **Product Sizing**:
   - 10 size variations (`US 7` to `US 12`) for every shoe model with real inventory stock.
5. **Buyer Active Cart**:
   - Pre-populated with 2 popular shoes so you can immediately test checkout.
6. **Live Tracking Orders**:
   - `SHOE-2026-892147`: Status **SHIPPED** (In Transit) — test the interactive "Advance Shipment Milestone" tracking progression button!
   - `SHOE-2026-773410`: Status **DELIVERED** — full 5-stage completed tracking journey.
   - `SHOE-2026-551092`: Status **PACKED** — packed at warehouse.

---

## 🛠️ Management Commands

- `python manage.py seed_demo`: Seeds the demo dataset.
- `python manage.py seed_demo --reset`: Cleans existing demo data and reseeds.
