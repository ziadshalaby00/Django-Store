import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from faker import Faker
from product.models import Product, Brand, Category

fake = Faker()
User = get_user_model()


def main():
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("No superuser found.")
        return

    brands = list(Brand.objects.all())
    categories = list(Category.objects.all())

    if not brands:
        print("No brands found.")
        return
    if not categories:
        print("No categories found.")
        return

    created = 0
    for _ in range(100):
        brand = random.choice(brands)
        category = random.choice(categories)
        name = f"{brand.name} {fake.word().title()} {random.randint(100, 999)}"
        price = round(random.uniform(50, 5000), 2)
        discount = random.randint(0, 40)
        stock = random.randint(5, 100)

        Product.objects.create(
            name=name,
            description=fake.paragraph(nb_sentences=3),
            price=price,
            discount_percentage=discount,
            stock=stock,
            brand=brand,
            category=category,
            created_by=admin,
            is_active=stock > 0,
        )
        created += 1

    print(f"Created {created} fake products.")


if __name__ == "__main__":
    main()