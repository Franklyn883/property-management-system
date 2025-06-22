from rest_framework import serializers
from .models import (
    UserProfile,
    CustomUser,
    OwnerProfile,
    ManagerProfile,
    AgentProfile,
    TenantProfile,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "role"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "id",
            "first_name",
            "last_name",
            "address",
            "city",
            "state",
            "country",
            "zip_code",
            "gender",
            "Date_of_birth",
        ]
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        # ✅ Safely update user only if user_data is provided
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # ✅ Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance