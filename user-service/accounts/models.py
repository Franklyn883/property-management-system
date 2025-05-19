from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import uuid
from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("occupant", "Occupant"),
            ("manager", "Manager"),
        ],
        default="user",
    )
    is_validated = models.BooleanField(default=False)
    pending_validation = models.BooleanField(default=False)
    # profile_image = models.ImageField(upload_to='profiles/', null=True,blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email
