from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserProfile,AgentProfile,ManagerProfile,OwnerProfile,TenantProfile
from .role_router import get_profile_for_user
User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

        """
        Creates a Profile object when a User is created.

        This function is connected to the post_save signal of the User model.
        It creates a Profile object when a User is created. The Profile object
        is associated with the User that triggered the signal.

        Args:
            sender (User): The User model that sent the signal.
            instance (User): The User instance that was created.
            created (bool): A boolean indicating whether a new object was created.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        if created:
            get_profile_for_user(instance).objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    It saves the Profile object associated with the User that triggered the

    signal.

    Args:
        sender (User): The User model that sent the signal.
        instance (User): The User instance that was saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    instance.get_profile_for_user(instance).save()

