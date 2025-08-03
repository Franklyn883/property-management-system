from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserProfile
from allauth.account.signals import email_confirmed

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


@receiver(email_confirmed)
def handle_email_confirmation(sender, email_address, **kwargs):
    """
    Sets the user's is_verified field to True when their email is confirmed by allauth.

    This signal is triggered when a user confirms their email address through allauth.
    """
    user = email_address.user
    if user and not user.is_verified:
        user.is_verified = True
        user.save(update_fields=["is_verified"])
