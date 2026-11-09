from django.core.management.base import BaseCommand
from store.seeds import seed_database


class Command(BaseCommand):
    help = 'Populates the database with realistic demo categories, shoes, users, carts, and tracking orders.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Wipes existing demo products, orders, categories, and demo users before reseeding.',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        
        self.stdout.write(self.style.NOTICE("Executing SoleVault demo seeder..."))
        try:
            seed_database(reset=reset, log=self.stdout.write)
            self.stdout.write(self.style.SUCCESS("Demo seeding completed successfully!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Seeding failed: {str(e)}"))
            raise e
