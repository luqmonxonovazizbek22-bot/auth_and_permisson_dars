from datetime import timedelta

from django.contrib.auth.models import UserManager, AbstractUser
from django.utils import timezone
from django.db import models
from root import settings


class User(AbstractUser):
    username = None
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=12, unique=True)   # 998901234567
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []


class PhoneCode(models.Model):
    LIFETIME = timedelta(minutes=5)
    MAX_ATTEMPTS = 5

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + self.LIFETIME