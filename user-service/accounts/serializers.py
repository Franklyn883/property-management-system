from rest_framework import serializers
from .models import (
    UserProfile,
    CustomUser,
)
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "role"]
        read_only_fields = [
            "id",
            "role",
        ]  # Role shouldn't be changed directly here


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
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def get_cleaned_data(self):
        
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }
    
    def save(self, request):
        # Use allauth's registration flow instead of creating user directly
        user = super().save(request)
        return user
