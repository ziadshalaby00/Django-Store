# import random
# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from faker import Faker
# from product.models import Product
# from reviews.models import Review

# fake = Faker()
# User = get_user_model()

# # تعليقات عربية للتقييمات
# ARABIC_POSITIVE_COMMENTS = [
#     "منتج رائع، أنصح الجميع به",
#     "جودة عالية وتصميم ممتاز",
#     "أفضل منتج اشتريته هذا العام",
#     "يستحق كل قرش دفعته فيه",
#     "شحن سريع ومنتج ممتاز",
#     "تفوق توقعاتي بكثير",
#     "جودة تصنيع عالية جداً",
#     "منتج عملي ومفيد جداً",
#     "التصميم أنيق والجودة عالية",
#     "أوصي بهذا المنتج بشدة",
#     "رائع! يعمل بشكل ممتاز",
#     "منتج مذهل، أشكركم على الجودة",
#     "تجربة شراء رائعة، سأشتري مرة أخرى",
#     "التغليف كان مثالياً والشحن سريع",
#     "لم أتوقع أن يكون بهذه الجودة الرائعة"
# ]

# ARABIC_NEUTRAL_COMMENTS = [
#     "منتج جيد لكن يمكن أن يكون أفضل",
#     "ليس سيئاً ولكن هناك مجال للتحسين",
#     "منتج متوسط المستوى",
#     "يؤدي الغرض لكنه ليس مميزاً",
#     "جيد لكن السعر مرتفع قليلاً",
#     "منتج عادي لا أكثر ولا أقل",
#     "لا بأس به ولكن هناك منتجات أفضل",
#     "متوسط الجودة، لا شيء خاص",
#     "يقوم بالعمل المطلوب ولكن دون إبهار"
# ]

# ARABIC_NEGATIVE_COMMENTS = [
#     "جودة أقل من المتوقع",
#     "لم يعجبني التصميم",
#     "الشحن تأخر كثيراً",
#     "المنتج لا يعمل كما هو مذكور",
#     "جودة التصنيع ضعيفة",
#     "لا أنصح بهذا المنتج",
#     "السعر لا يتناسب مع الجودة",
#     "المنتج به عيوب تصنيع",
#     "تجربة مخيبة للآمال",
#     "المنتج معيب ولا يعمل بشكل صحيح"
# ]

# # تعليقات إنجليزية للتقييمات
# ENGLISH_POSITIVE_COMMENTS = [
#     "Excellent product, highly recommended!",
#     "Great quality and amazing design",
#     "Best product I've bought this year",
#     "Worth every penny I paid for it",
#     "Fast shipping and excellent product",
#     "Exceeded my expectations by far",
#     "Very high manufacturing quality",
#     "Practical and very useful product",
#     "Elegant design and high quality",
#     "I highly recommend this product",
#     "Awesome! Works perfectly",
#     "Amazing product, thank you for the quality",
#     "Great shopping experience, I will buy again",
#     "Packaging was perfect and shipping was fast",
#     "Didn't expect it to be this amazing quality"
# ]

# ENGLISH_NEUTRAL_COMMENTS = [
#     "Good product but could be better",
#     "Not bad but there's room for improvement",
#     "Average product",
#     "Does the job but not exceptional",
#     "Good but the price is a bit high",
#     "Ordinary product, nothing more nothing less",
#     "Okay but there are better products",
#     "Average quality, nothing special",
#     "Does the required work but without impressing"
# ]

# ENGLISH_NEGATIVE_COMMENTS = [
#     "Quality lower than expected",
#     "Didn't like the design",
#     "Shipping was very delayed",
#     "Product doesn't work as described",
#     "Poor manufacturing quality",
#     "I don't recommend this product",
#     "Price doesn't match the quality",
#     "Product has manufacturing defects",
#     "Disappointing experience",
#     "Defective product, doesn't work properly"
# ]

# class Command(BaseCommand):
#     help = "Create realistic fake reviews for products in Arabic and English"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--min_reviews',
#             type=int,
#             default=5,
#             help='Minimum number of reviews per product'
#         )
#         parser.add_argument(
#             '--max_reviews',
#             type=int,
#             default=30,
#             help='Maximum number of reviews per product'
#         )

#     def handle(self, *args, **options):
#         min_reviews = options['min_reviews']
#         max_reviews = options['max_reviews']
        
#         products = list(Product.objects.all())
#         users = list(User.objects.all())
        
#         if not products:
#             self.stdout.write(self.style.ERROR("No products found. Create products first."))
#             return
            
#         if not users:
#             self.stdout.write(self.style.ERROR("No users found. Create users first."))
#             return
        
#         total_reviews_created = 0
        
#         for product in products:
#             # عدد التقييمات لهذا المنتج (بين min_reviews و max_reviews)
#             num_reviews = random.randint(min_reviews, max_reviews)
            
#             # اختيار مستخدمين عشوائيين للتقييم (مع عدم التكرار)
#             available_users = [user for user in users if not Review.objects.filter(product=product, user=user).exists()]
#             reviewers = random.sample(available_users, min(num_reviews, len(available_users)))
            
#             for user in reviewers:
#                 try:
#                     # تحديد التقييم (توزيع واقعي: معظم التقييمات إيجابية)
#                     rating_options = [5, 5, 5, 4, 4, 4, 3, 3, 2, 1]
#                     rating = random.choice(rating_options)
                    
#                     # اختيار لغة التعليق (عربي أو إنجليزي)
#                     is_arabic = random.choice([True, False])
                    
#                     # اختيار التعليق بناء على التقييم واللغة
#                     if rating >= 4:
#                         comment = random.choice(ARABIC_POSITIVE_COMMENTS if is_arabic else ENGLISH_POSITIVE_COMMENTS)
#                     elif rating == 3:
#                         comment = random.choice(ARABIC_NEUTRAL_COMMENTS if is_arabic else ENGLISH_NEUTRAL_COMMENTS)
#                     else:
#                         comment = random.choice(ARABIC_NEGATIVE_COMMENTS if is_arabic else ENGLISH_NEGATIVE_COMMENTS)
                    
#                     # أحياناً لا نضع تعليق (20% من الحالات)
#                     if random.random() < 0.2:
#                         comment = ""
#                     else:
#                         if random.random() < 0.3:  # 30% من الحالات
#                             comment += " " + fake.paragraph(nb_sentences=2)
                    
#                     # إنشاء التقييم
#                     Review.objects.create(
#                         product=product,
#                         user=user,
#                         rating=rating,
#                         comment=comment
#                     )
                    
#                     total_reviews_created += 1
                    
#                 except Exception as e:
#                     self.stdout.write(self.style.ERROR(f"Error creating review for product {product.name} by user {user.username}: {e}"))
            
#             self.stdout.write(self.style.SUCCESS(f"Created {len(reviewers)} reviews for product: {product.name}"))
        
#         self.stdout.write(self.style.SUCCESS(f"Successfully created {total_reviews_created} reviews for {len(products)} products"))