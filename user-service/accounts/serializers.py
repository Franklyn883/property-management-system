from rest_framework import serializers
from .models import (
    UserProfile,
    CustomUser,
)
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from datetime import datetime
from .validation import (
    PasswordStrengthValidator,
    EmailDomainValidator,
    PhoneNumberValidator,
    NameValidator,
    AgeValidator,
    URLValidator,
    ValidationMixin,
)


class CustomUserSerializer(serializers.ModelSerializer, ValidationMixin):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "role", "is_verified"]
        read_only_fields = [
            "id",
            "role",
            "is_verified",
        ]
    
    def validate_email(self, value):
        """Validate email format and domain."""
        return self.validate_email_domain(value)
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value:
            return self.validate_phone_number(value)
        return value


class UserProfileSerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Base serializer for the UserProfile model.
    Handles nested update of the CustomUser.
    """

    user = CustomUserSerializer()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "first_name",
            "last_name",
            "avatar_url",
            "bio",
            "gender",
            "date_of_birth",
            "address",
            "city",
            "state",
            "country",
            "zip_code",
            "notification_preferences",
            "saved_searches",
            "wishlist",
            "is_verified_poster",
            "poster_verification_status",
            "verified_at",
            "poster_documents",
        ]
        read_only_fields = [
            "is_verified_poster",
            "poster_verification_status",
            "verified_at",
        ]

    def validate_first_name(self, value):
        """Validate first name using NameValidator."""
        return self.validate_name(value)

    def validate_last_name(self, value):
        """Validate last name using NameValidator."""
        return self.validate_name(value)

    def validate_date_of_birth(self, value):
        """Validate date of birth using AgeValidator."""
        if value:
            return self.validate_age(value)
        return value

    def validate_avatar_url(self, value):
        """Validate avatar URL using URLValidator."""
        if value:
            return self.validate_url(value)
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        # Update the related CustomUser instance
        if user_data:
            user_serializer = CustomUserSerializer(
                instance.user, data=user_data, partial=True
            )
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        # Update the UserProfile instance for the remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AgentProfileSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            "agency_name",
            "license_id",
            "license_expiration_date",
            "license_documents",
            "clients_managed_count",
        ]

    def validate_license_expiration_date(self, value):
        """
        Validate the license expiration date.
        """
        if value and value < datetime.now().date():
            raise serializers.ValidationError(
                "License expiration date cannot be in the past"
            )
        return value

    def validate_license_id(self, value):
        """
        Validate the license ID.
        """
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "License ID must be at least 10 characters long"
            )
        return value.strip() if value else None

    def validate_agency_name(self, value):
        """
        Validate the agency name.
        """
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Agency name must be at least 3 characters long"
            )
        return value.strip() if value else None


class ManagerProfileSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            "properties_managed_count",
            "assigned_properties",
            "maintenance_requests_handled_count",
            "assigned_maintenance_requests",
        ]


class TenantProfileSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            "tenant_documents",
            "properties_rented_count",
            "rental_history_rating",
            "preferred_locations",
        ]

    def validate_rental_history_rating(self, value):
        """
        Validate the rental history rating.
        """
        if value and (value < 0 or value > 5):
            raise serializers.ValidationError(
                "Rental history rating must be between 1 and 5"
            )
        return value


class OwnerProfileSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            "ownership_documents",
            "properties_owned_count",
        ]


class CustomRegisterSerializer(RegisterSerializer, ValidationMixin):
    """
    Custom register serializer that works with allauth email verification
    """

    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Validate email format and domain."""
        return self.validate_email_domain(value)

    def validate_password1(self, value):
        """Validate password strength."""
        return self.validate_password_strength(value)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def get_cleaned_data(self):

        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self, request):
        # Use allauth's registration flow instead of creating user directly
        user = super().save(request)
        return user


class VerificationSubmissionSerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for poster verification submission.
    """

    document_type = serializers.ChoiceField(
        choices=[
            ("identity", "Identity Document"),
            ("ownership", "Property Ownership Document"),
            ("license", "Real Estate License"),
            ("business", "Business Registration"),
            ("other", "Other"),
        ]
    )
    document_name = serializers.CharField(max_length=255)
    document_url = serializers.URLField(help_text="URL of the document file")
    description = serializers.CharField(max_length=500, required=False)

    def validate_document_url(self, value):
        """Validate document URL using URLValidator."""
        return self.validate_url(value)


class VerificationStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for verification status.
    """
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    can_post_property = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "is_verified_poster",
            "poster_verification_status",
            "verified_at",
            "user_email",
            "user_role",
            "can_post_property",
        ]

    def get_can_post_property(self, obj):
        """
        Determine if the user can post property.
        """
        return obj.can_post_property


class AdminVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for admin verification management.
    """
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    full_name = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user_email",
            "user_role",
            "full_name",
            "is_verified_poster",
            "poster_verification_status",
            "poster_documents",
            "verified_at",
            "date_joined",
        ]

    def get_full_name(self, obj):
        """
        Get the full name of the user.
        """
        return obj.get_full_name


class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user listing with basic user information.
    """
    full_name = serializers.SerializerMethodField()
    profile_id = serializers.UUIDField(source='profile.id', read_only=True)
    is_verified_poster = serializers.BooleanField(source='profile.is_verified_poster', read_only=True)
    poster_verification_status = serializers.CharField(source='profile.poster_verification_status', read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'phone_number',
            'role',
            'is_active',
            'is_verified',
            'is_staff',
            'full_name',
            'profile_id',
            'is_verified_poster',
            'poster_verification_status',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.profile.first_name} {obj.profile.last_name}".strip()
        except:
            return ""


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user detail with comprehensive user information.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    is_verified_poster = serializers.BooleanField(source='profile.is_verified_poster', read_only=True)
    poster_verification_status = serializers.CharField(source='profile.poster_verification_status', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'phone_number',
            'role',
            'is_active',
            'is_verified',
            'is_staff',
            'full_name',
            'profile',
            'is_verified_poster',
            'poster_verification_status',
            'date_joined',
            'last_login',
            'updated_at',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'updated_at']

    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.profile.first_name} {obj.profile.last_name}".strip()
        except:
            return ""


class AdminUserActionSerializer(serializers.Serializer):
    """
    Serializer for admin user actions like role change, activation, etc.
    """
    role = serializers.ChoiceField(
        choices=CustomUser._meta.get_field('role').choices,
        required=False,
        help_text="New role for the user"
    )
    is_active = serializers.BooleanField(
        required=False,
        help_text="Whether the user account is active"
    )
    is_staff = serializers.BooleanField(
        required=False,
        help_text="Whether the user has staff privileges"
    )
    is_verified = serializers.BooleanField(
        required=False,
        help_text="Whether the user's email is verified"
    )

    def validate_role(self, value):
        """Validate role change."""
        if value == 'admin':
            raise serializers.ValidationError("Cannot change user role to admin via API")
        return value
