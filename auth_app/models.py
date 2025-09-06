from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    fullname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username