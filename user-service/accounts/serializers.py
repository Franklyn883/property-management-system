from rest_framework import serializers
from .models import (
    UserProfile,
    CustomUser,
)
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from datetime import datetime


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "role", "is_verified"]
        read_only_fields = [
            "id",
            "role",
            "is_verified",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
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

    def validate_name(self, value):
        """
        Validate the first and last name.
        """
        if not value.strip() or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters long"
            )
        return value.strip()

    def validate_date_of_birth(self, value):
        """
        Validate the date of birth.
        """
        if value and value > datetime.now().date():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future"
            )
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


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom register serializer that works with allauth email verification
    """

    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

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


class VerificationSubmissionSerializer(serializers.Serializer):
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
        """
        Validate the document URL format.
        """
        valid_schemes = ["https://", "http://", "localhost"]
        if not any(value.startswith(scheme) for scheme in valid_schemes):
            raise serializers.ValidationError(
                "Document URL must be a valid HTTP/HTTPS URL"
            )
        return value


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
