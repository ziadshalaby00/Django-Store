import os, django, random
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from product.models import Product
from reviews.models import Review

User = get_user_model()

COMMENTS = [
    "منتج رائع، أنصح الجميع به",
    "جودة عالية وتصميم ممتاز",
    "Excellent product, highly recommended!",
    "Great quality and amazing design",
    "منتج جيد لكن يمكن أن يكون أفضل",
    "Good product but could be better",
    "جودة أقل من المتوقع",
    "Quality lower than expected",
    "Worth every penny I paid for it",
    "يستحق كل قرش دفعته فيه",
]

products = list(Product.objects.all())
users = list(User.objects.all())

if not products or not users:
    print("Need products and users first!")
    exit()

created = 0
for product in products:
    count = random.randint(3, 10)
    sample_users = random.sample(users, min(count, len(users)))

    for user in sample_users:
        if Review.objects.filter(product=product, user=user).exists():
            continue

        Review.objects.create(
            product=product,
            user=user,
            rating=random.choice([5,5,5,4,4,4,3,3,2,1]),
            comment=random.choice(COMMENTS)
        )
        created += 1

print(f"Created {created} reviews for {len(products)} products.")