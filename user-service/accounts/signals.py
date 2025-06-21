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

        profile = get_profile_for_user(instance)
        
        if created:
            profile.objects.create(user=instance)
            
        else:
            profile, _ = profile.objects.get_or_create(user=instance)
            profile.save()
            
