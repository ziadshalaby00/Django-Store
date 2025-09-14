# import random
# import time
# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from faker import Faker
# from product.models import Product, ProductImage, Brand, Category
# import requests
# from django.core.files.base import ContentFile
# from django.db import transaction

# fake = Faker()
# User = get_user_model()
# TOTAL_PRODUCTS = 100

# PIXABAY_API_KEY = "32386872-6082da82f8585377416a1336a"
# REQUEST_DELAY = 0.5  # تأخير بين الطلبات لتجنب حظر API

# CATEGORY_IMAGE_KEYWORDS = {
#     "Tech Accessories": "tech+gadgets+electronic",
#     "Headphones and audio devices": "headphones+audio+music",
#     "Glasses and lighting": "eyeglasses+lighting+desk",
#     "Watches and wearable accessories": "smartwatch+wearable+technology",
#     "Personal Organization Tools and Supplies": "office+organizer+desk"
# }

# def get_pixabay_image_url(category_name, retries=3):
#     """الحصول على صورة من Pixabay مع إعادة المحاولة"""
#     keyword = CATEGORY_IMAGE_KEYWORDS.get(category_name, "electronics")
#     url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={keyword}&image_type=photo&per_page=50&safesearch=true"
    
#     for attempt in range(retries):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 hits = data.get("hits", [])
#                 if hits:
#                     # تجنب الصور ذات الأحجام الكبيرة جداً
#                     valid_hits = [hit for hit in hits if hit.get("webformatURL")]
#                     if valid_hits:
#                         return random.choice(valid_hits).get("webformatURL")
#             time.sleep(1)  # انتظار قبل إعادة المحاولة
#         except (requests.RequestException, ConnectionError) as e:
#             print(f"Pixabay API attempt {attempt + 1} failed: {e}")
#             time.sleep(2)
    
#     return None

# def download_image(url, timeout=15):
#     """تحميل الصورة مع معالجة الأخطاء"""
#     try:
#         response = requests.get(url, timeout=timeout)
#         response.raise_for_status()
#         return response.content
#     except requests.RequestException as e:
#         print(f"Failed to download image: {e}")
#         return None

# class Command(BaseCommand):
#     help = "Populate 100 products with images from Pixabay"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--total',
#             type=int,
#             default=TOTAL_PRODUCTS,
#             help='Number of products to create'
#         )

#     @transaction.atomic
#     def handle(self, *args, **kwargs):
#         total_products = kwargs.get('total', TOTAL_PRODUCTS)
        
#         try:
#             user = User.objects.get(username="admin")
#         except User.DoesNotExist:
#             self.stdout.write(self.style.ERROR("User 'admin' does not exist. Create it first."))
#             return

#         brands = list(Brand.objects.all())
#         categories = list(Category.objects.all())

#         if not brands:
#             self.stdout.write(self.style.ERROR("No brands found. Create brands first."))
#             return
#         if not categories:
#             self.stdout.write(self.style.ERROR("No categories found. Create categories first."))
#             return

#         created_count = 0
#         failed_count = 0

#         for i in range(total_products):
#             category = random.choice(categories)
#             brand = random.choice(brands)
#             product_name = f"{brand.name} {fake.word().title()} {random.randint(100,999)}"
            
#             product = Product(
#                 name=product_name,
#                 description=fake.paragraph(nb_sentences=3),
#                 price=round(random.uniform(10, 500), 2),
#                 discount_percentage=random.randint(0, 30),
#                 stock=random.randint(10, 100),
#                 brand=brand,
#                 category=category,
#                 created_by=user,
#             )

#             # الحصول على صورة رئيسية
#             main_image_url = get_pixabay_image_url(category.name)
#             if main_image_url:
#                 image_content = download_image(main_image_url)
#                 if image_content:
#                     product.image.save(
#                         f"{product_name.replace(' ', '_')}_{i}.jpg",
#                         ContentFile(image_content),
#                         save=False
#                     )
#                 else:
#                     self.stdout.write(self.style.WARNING(f"Failed to download main image for {product_name}"))
#                     failed_count += 1
#                     continue
#             else:
#                 self.stdout.write(self.style.WARNING(f"No main image found for {category.name}"))
#                 failed_count += 1
#                 continue

#             # حفظ المنتج
#             product.save()
            
#             # إضافة صور فرعية (1-3 صور)
#             sub_images_count = random.randint(1, 3)
#             sub_images_created = 0
            
#             for j in range(sub_images_count):
#                 sub_image_url = get_pixabay_image_url(category.name)
#                 if sub_image_url:
#                     image_content = download_image(sub_image_url)
#                     if image_content:
#                         ProductImage.objects.create(
#                             product=product,
#                             image=ContentFile(
#                                 image_content, 
#                                 name=f"{product_name.replace(' ', '_')}_{i}_sub{j+1}.jpg"
#                             )
#                         )
#                         sub_images_created += 1
#                         time.sleep(REQUEST_DELAY)  # تأخير بين الطلبات

#             created_count += 1
#             self.stdout.write(self.style.SUCCESS(f"Created product {created_count}/{total_products}"))
            
#             # تأخير بين المنتجات لتجنب إغراق API
#             time.sleep(REQUEST_DELAY)

#         self.stdout.write(self.style.SUCCESS(
#             f"Successfully created {created_count} products. Failed: {failed_count}"
#         ))