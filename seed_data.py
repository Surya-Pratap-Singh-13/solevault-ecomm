#!/usr/bin/env python
"""
Standalone Seeder Script for SoleVault.
Can be executed directly:
    python seed_data.py
Or with reset flag:
    python seed_data.py --reset
"""
import os
import sys
import argparse
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoestore.settings')
django.setup()

from store.seeds import seed_database


def main():
    parser = argparse.ArgumentParser(description="Seed database with demo products, users, cart, and orders.")
    parser.add_argument('--reset', action='store_true', help="Clear old demo data before reseeding.")
    args = parser.parse_args()

    seed_database(reset=args.reset)


if __name__ == '__main__':
    main()
