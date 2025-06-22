from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import uuid
from .managers import CustomUserManager
from django.contrib.auth import get_user_model


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where email is the unique identifiers
    for authentication instead of usernames.

    This model has the following fields:
        - id: the primary key of the user, a UUID
        - email: the email address of the user, used for authentication
        - phone_number: the phone number of the user, used for verification
        - role: the role of the user, one of the following: user, owner, manager, admin, agent, tenant

    """

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("owner", "Owner"),
            ("manager", "Manager"),
            ("admin", "Admin"),
            ("agent", "Agent"),
            ("tenant", "Tenant"),
        ],
        default="user",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether the user has verified their email address.",
    )
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    pending_validation = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    User profile model where user details are stored.

    This model has the following fields:
        - user: the user instance related to the profile
        - first_name: the first name of the user
        - last_name: the last name of the user
        - avatar_url: the URL of the user's avatar
        - bio: the biography of the user
        - gender: the gender of the user, one of the following: male, female, other
        - Date_of_birth: the date of birth of the user
        - notification_preferences: the notification preferences of the user
        - address: the address of the user
        - city: the city of the user
        - state: the state of the user
        - country: the country of the user
        - zip_code: the zip code of the user
        - created_at: the time the profile was created
    """

    User = get_user_model()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    saved_searches = models.JSONField(null=True, blank=True)
    wishlist = models.JSONField(null=True, blank=True)
    gender = models.CharField(
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        null=True,
        blank=True,
    )
    Date_of_birth = models.DateField(null=True, blank=True)
    notification_preferences = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Notification preferences",
        verbose_name="Notification Preferences",
    )
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_poster = models.BooleanField(
        default=False, help_text="Whether the poster is verified or not"
    )
    poster_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    poster_documents = models.JSONField(
        null=True, blank=True, help_text="Documents uploaded by the poster"
    )

    @property
    def get_full_name(self):
        """
        Returns the full name of the user.

        Returns:
            str: The full name of the user.
        str: The full name of the user.
        """

        return f"{self.first_name} {self.last_name}"

    @property
    def can_post_property(self):
        """
        Determines if the user can post a property based on their role and verification status.

        Returns:
        bool: True if the user role is either "owner" or "agent" and the user is verified, otherwise False.
        """
        return self.user.role in ["owner", "agent"] and self.is_verified_poster

    def __str__(self):
        return self.user.email


class AgentProfile(UserProfile):
    """
    Agent profile model where agent details are stored.

    This model has the following fields:
        - license_id: the agent's license ID
        - license_expiration_date: the expiration date of the agent's license
        - license_documents: documents uploaded by the agent
        - clients_managed_count: the count of clients managed by the agent
        - agency_name: the name of the agency the agent is associated with
    """

    license_id = models.CharField(max_length=20, null=True, blank=True)
    license_expiration_date = models.DateField(null=True, blank=True)
    license_documents = models.JSONField(
        null=True, blank=True, help_text="Documents uploaded by the agent"
    )
    clients_managed_count = models.PositiveIntegerField(default=0)
    agency_name = models.CharField(max_length=100, null=True, blank=True)


class OwnerProfile(UserProfile):
    """
    Owner profile model where owner details are stored.
    """

    ownership_documents = models.JSONField(
        null=True, blank=True, help_text="Documents uploaded by the owner"
    )
    properties_owned_count = models.PositiveIntegerField(default=0)


class TenantProfile(UserProfile):
    """
    Tenant profile model where tenant details are stored
    """

    tenant_documents = models.JSONField(
        null=True, blank=True, help_text="Documents uploaded by the tenant"
    )
    properties_rented_count = models.PositiveIntegerField(default=0)
    rental_history_rating = models.PositiveIntegerField(default=0)
    preferred_locations = models.JSONField(
        null=True, blank=True, help_text="Preferred locations for renting"
    )


class ManagerProfile(UserProfile):
    """
    Manager profile model where manager details are stored
    """

    properties_managed_count = models.PositiveIntegerField(default=0)
    assigned_properties = models.JSONField(
        null=True, blank=True, help_text="Properties managed by the manager"
    )
    maintainces_requests_handled_count = models.PositiveIntegerField(default=0)
    assigned_maintainces_requests = models.JSONField(
        null=True,
        blank=True,
        help_text="Maintainces requests handled by the manager",
    )
