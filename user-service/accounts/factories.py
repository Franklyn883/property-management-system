"""Test factories for creating test data objects."""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from .models import UserProfile
import uuid

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = factory.Iterator(['owner', 'agent', 'tenant', 'manager'])
    is_verified = True
    is_active = True


class AdminUserFactory(UserFactory):
    """Factory for creating Admin User instances."""
    role = 'admin'
    is_staff = True
    is_superuser = True


class UserProfileFactory(DjangoModelFactory):
    """Factory for creating UserProfile instances."""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = '+1234567890'
    is_verified_poster = False 