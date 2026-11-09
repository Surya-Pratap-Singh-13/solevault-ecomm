from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from store.models import Category, Product, ProductSize, Cart, Order
from store.seeds import seed_database


class DemoSeedTest(TestCase):
    def test_seed_database_execution(self):
        """Test that seed_database creates the expected demo entities."""
        seed_database()

        self.assertTrue(User.objects.filter(username='admin', is_superuser=True).exists())
        self.assertTrue(User.objects.filter(username='buyer').exists())
        self.assertGreaterEqual(Category.objects.count(), 6)
        self.assertGreaterEqual(Product.objects.count(), 12)
        self.assertGreaterEqual(ProductSize.objects.count(), 100)
        self.assertGreaterEqual(Order.objects.count(), 3)

        buyer = User.objects.get(username='buyer')
        self.assertTrue(Cart.objects.filter(user=buyer).exists())
        self.assertGreaterEqual(Cart.objects.get(user=buyer).items.count(), 1)

    def test_management_command_seed_demo(self):
        """Test calling the management command via call_command."""
        call_command('seed_demo', reset=True)
        self.assertTrue(Product.objects.filter(slug='air-vapormax-flyknit-blaze').exists())

