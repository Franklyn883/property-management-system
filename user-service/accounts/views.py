from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError

from .role_router import get_serializer_for_user
from .models import UserProfile

User = get_user_model()


# Create your views here.
class InternalUserDetailView(APIView):
    """Returns the user details"""

    def get(self, request, user_id):
        """Returns the user details of the user_id."""
        api_key = request.headers.get("X-Internal-Api-Key")
        if api_key != settings.INTERNAL_API_KEY:
            return Response(
                {"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id)
            user_data = {
                "id": user.id,
                "email": user.email,
                # add other fields as needed
            }
            return Response(user_data)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class Profile(APIView):
    """
    Profile management endpoint that handles role-based profile data.

    GET: Returns the user profile based on the user's role.
    PUT/PATCH: Updates the user profile based on the user's role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns the user profile based on the user's role.
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # Get the serializer for the user's role
        serializer_class = get_serializer_for_user(request.user)
        serializer = serializer_class(profile)

        return Response(
            {
                "status": "success",
                "data": serializer.data,
                "user_role": request.user.role,
                "is_verified_poster": getattr(
                    profile, "is_verified_poster", False
                ),
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        """
        Updates the user profile based on the user's role.
        """
        return self._update_profile(request, partial=False)

    def patch(self, request):
        """
        Updates the user profile based on the user's role.
        """
        return self._update_profile(request, partial=True)

    def _update_profile(self, request, partial=False):
        """
        Helper method to update the user profile.
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get the serializer for the user's role
        serializer_class = get_serializer_for_user(request.user)

        try:
            with transaction.atomic():
                serializer = serializer_class(
                    profile, data=request.data, partial=partial
                )

                if serializer.is_valid():
                    # Addition role-specific validation
                    validation_errors = self._validate_role_specific_data(
                        request.user, serializer.validated_data
                    )
                    if validation_errors:
                        return Response(
                            {
                                "status": "error",
                                "errors": validation_errors,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    serializer.save()

                    return Response(
                        {
                            "status": "success",
                            "message": "Profile updated successfully",
                            "data": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "status": "error",
                            "errors": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "errors": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "error": "An error occurred while updating the profile",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _validate_role_specific_data(self, user, validated_data):
        """
        Validates role-specific data for the user.
        """
        role = user.role

        # Agent role validation
        if role == "agent":
            if (
                "license_id" in validated_data
                and not validated_data["license_id"]
            ):
                return {"license_id": ["This field is required for agents"]}
            if (
                "agency_name" in validated_data
                and not validated_data["agency_name"]
            ):
                return {"agency_name": ["This field is required for agents"]}

        # Owner-specific validation
        elif role == "owner":
            pass

        # Manager-specific validation
        elif role == "manager":
            pass

        # Tenant-specific validation
        elif role == "tenant":
            pass

        return None

    def _get_profile_instance(self, user):
        """
        Returns the profile instance for the user.
        """
        try:
            return user.profile
        except UserProfile.DoesNotExist:
            return None
