from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import uuid
from .managers import CustomUserManager
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where email is the unique identifiers
    for authentication instead of usernames.
p
        - email: the email address of the user, used for authentication
        - phone_number: the phone number of the user, used for verification
        - role: the role of the user, one of the following: user, owner, manager, admin, agent, tenant

    """

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
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

    # Add the missing is_staff field
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    A single, consolidated user profile model that stores all user details.
    Role-specific fields are nullable and are only used when the user has the corresponding role.
    """

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="profile"
    )

    # --- Common Profile Fields ---
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(
        null=True, blank=True
    )  # Renamed for consistency
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    notification_preferences = models.JSONField(
        null=True, blank=True, default=dict
    )
    saved_searches = models.JSONField(null=True, blank=True)
    wishlist = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Verification Fields (Common to posters like Owner/Agent) ---
    is_verified_poster = models.BooleanField(default=False)
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
    poster_documents = models.JSONField(null=True, blank=True)

    # --- Agent-specific Fields ---
    agency_name = models.CharField(max_length=100, null=True, blank=True)
    license_id = models.CharField(max_length=20, null=True, blank=True)
    license_expiration_date = models.DateField(null=True, blank=True)
    license_documents = models.JSONField(
        null=True, blank=True, help_text="Agent license documents"
    )
    clients_managed_count = models.PositiveIntegerField(default=0)

    # --- Owner-specific Fields ---
    ownership_documents = models.JSONField(
        null=True, blank=True, help_text="Owner ownership documents"
    )
    properties_owned_count = models.PositiveIntegerField(default=0)

    # --- Tenant-specific Fields ---
    tenant_documents = models.JSONField(
        null=True, blank=True, help_text="Tenant documents"
    )
    properties_rented_count = models.PositiveIntegerField(default=0)
    rental_history_rating = models.PositiveIntegerField(default=0)
    preferred_locations = models.JSONField(null=True, blank=True)

    # --- Manager-specific Fields ---
    properties_managed_count = models.PositiveIntegerField(default=0)
    assigned_properties = models.JSONField(null=True, blank=True)
    maintenance_requests_handled_count = models.PositiveIntegerField(
        default=0
    )  # Renamed for clarity
    assigned_maintenance_requests = models.JSONField(
        null=True, blank=True
    )  # Renamed for clarity

    @property
    def get_full_name(self):
        """
        Returns the full name of the user.
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def can_post_property(self):
        """
        Determines if the user can post a property based on their role and verification status.
        """
        return self.user.role in ["owner", "agent"] and self.is_verified_poster

    def submit_verification_document(self, document_data):
        """
        Submit a verification document for the user.
        """
        if self.poster_documents is None:
            self.poster_documents = []

        document_data["id"] = str(uuid.uuid4())
        document_data["submitted_at"] = timezone.now().isoformat()
        self.poster_documents.append(document_data)
        self.poster_verification_status = "pending"
        self.save()

    def approve_verification(self, approve_by):
        """
        Approve the verification for the user.
        """
        self.poster_verification_status = "approved"
        self.verified_at = timezone.now()
        self.is_verified_poster = True

    def reject_verification(self, reject_by, reason):
        """
        Reject the verification for the user.
        """
        self.poster_verification_status = "rejected"
        self.verified_at = None
        self.is_verified_poster = False

        if self.poster_documents is None:
            self.poster_documents = []

        rejection_data = {
            "id": str(uuid.uuid4()),
            "type": "rejection",
            "reason": reason,
            "rejected_at": timezone.now().isoformat(),
            "rejected_by": reject_by,
        }
        self.poster_documents.append(rejection_data)
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.get_full_name}"


class FailedLoginAttempt(models.Model):
    """
    Model to track failed login attempts for account lockout.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='failed_login_attempts',
        null=True,
        blank=True
    )
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)
    lockout_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email', 'ip_address']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Failed login: {self.email} from {self.ip_address} at {self.timestamp}"
    
    @classmethod
    def is_ip_locked(cls, ip_address):
        """Check if IP is locked due to too many failed attempts."""
        cutoff_time = timezone.now() - timedelta(minutes=15)
        recent_attempts = cls.objects.filter(
            ip_address=ip_address,
            timestamp__gte=cutoff_time
        ).count()
        return recent_attempts >= 10  # Lock after 10 failed attempts in 15 minutes
    
    @classmethod
    def is_email_locked(cls, email):
        """Check if email is locked due to too many failed attempts."""
        cutoff_time = timezone.now() - timedelta(minutes=30)
        recent_attempts = cls.objects.filter(
            email=email,
            timestamp__gte=cutoff_time
        ).count()
        return recent_attempts >= 5  # Lock after 5 failed attempts in 30 minutes


class UserSession(models.Model):
    """
    Model to track user sessions for security monitoring.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Session: {self.user.email} from {self.ip_address}"
    
    @classmethod
    def cleanup_old_sessions(cls, days=30):
        """Clean up sessions older than specified days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        cls.objects.filter(last_activity__lt=cutoff_date).delete()


class BlockedIP(models.Model):
    """
    Model to track blocked IP addresses.
    """
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    blocked_at = models.DateTimeField(auto_now_add=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    blocked_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocked_ips'
    )
    
    class Meta:
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['blocked_until']),
        ]
    
    def __str__(self):
        return f"Blocked IP: {self.ip_address} - {self.reason}"
    
    @classmethod
    def is_ip_blocked(cls, ip_address):
        """Check if IP is currently blocked."""
        now = timezone.now()
        return cls.objects.filter(
            ip_address=ip_address
        ).filter(
            models.Q(is_permanent=True) |
            models.Q(blocked_until__isnull=True) |
            models.Q(blocked_until__gt=now)
        ).exists()
    
    @classmethod
    def cleanup_expired_blocks(cls):
        """Remove expired IP blocks."""
        now = timezone.now()
        cls.objects.filter(
            is_permanent=False,
            blocked_until__lt=now
        ).delete()


class SecurityAuditLog(models.Model):
    """
    Model to log security-related events.
    """
    EVENT_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('account_lockout', 'Account Lockout'),
        ('ip_block', 'IP Block'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('admin_action', 'Admin Action'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_audit_logs'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()}: {self.user.email if self.user else 'Unknown'} at {self.timestamp}"
    
    @classmethod
    def log_event(cls, event_type, user=None, ip_address=None, user_agent=None, details=None):
        """Log a security event."""
        return cls.objects.create(
            event_type=event_type,
            user=user,
            ip_address=ip_address or '0.0.0.0',
            user_agent=user_agent or '',
            details=details or {}
        )
