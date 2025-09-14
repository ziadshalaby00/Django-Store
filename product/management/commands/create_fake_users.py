import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = "Create 100 fake users with fullname field"

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=100,
            help='Number of users to create'
        )

    def handle(self, *args, **options):
        total_users = options['total']
        created_count = 0
        
        for i in range(total_users):
            # إنشاء اسم كامل عشوائي
            fullname = fake.name()
            
            # إنشاء اسم مستخدم فريد بناء على الاسم الكامل
            base_username = ''.join(e for e in fullname.lower() if e.isalnum())
            username = f"{base_username}{random.randint(100, 999)}"
            
            # إنشاء بريد إلكتروني فريد
            email = f"{username}@example.com"
            
            # إنشاء كلمة مرور (نفس اسم المستخدم)
            password = username
            
            # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                try:
                    # إنشاء المستخدم مع حقل fullname
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        fullname=fullname  # استخدام حقل fullname
                    )
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created user: {username} - {fullname}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating user {username}: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {username} already exists, skipping..."))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} users out of {total_users} requested"))