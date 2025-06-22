from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile object automatically when a new User is created.

    This function is connected to the post_save signal of the User model.
    When a new User is created, this signal creates a corresponding UserProfile
    and associates it with the new user.
    """
    if created:
        UserProfile.objects.create(user=instance)
