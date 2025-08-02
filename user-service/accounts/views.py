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
from rest_framework.viewsets import ViewSet
from .utility import get_serializer_for_user, get_profile_for_user
from .models import UserProfile
from .serializers import (
    VerificationSubmissionSerializer,
    VerificationStatusSerializer,
    AdminVerificationSerializer,
)
from .permissions import IsOwnerOrAgent, IsAdmin
from django.utils import timezone
from rest_framework.decorators import action
import uuid
from django.db.models import Q
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination

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
        profile = get_profile_for_user(request)
        if profile is None:
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
        profile = get_profile_for_user(request)
        if profile is None:
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
        
        


class VerificationViewSet(ViewSet):
    """
    Viewset for poster verification management.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], permission_classes=[IsOwnerOrAgent])
    def submit(self, request):
        """
        Submit a verification document for the user.
        """
        profile = self._get_profile_or_error(request)
        if isinstance(profile, Response):
            return profile

        if profile.is_verified_poster:
            return self._error_response("User already verified", status.HTTP_400_BAD_REQUEST)

        serializer = VerificationSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.poster_documents is None:
                        profile.poster_documents = []

                    document_data = {
                        "id": str(uuid.uuid4()),
                        "submitted_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }

                    profile.poster_documents.append(document_data)
                    profile.poster_verification_status = "pending"
                    profile.save()

                    return Response(
                        {
                            "status": "success",
                            "message": "Verification document submitted successfully",
                            "verification_status": "pending",
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                import logging
                logging.error(f"Error submitting verification document for user {getattr(profile.user, 'email', None)}: {e}")
                return self._error_response(
                    "An error occurred while submitting the verification document",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {
                    "status": "error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _get_profile_or_error(self, request):
        profile = get_profile_for_user(request)
        if profile is None:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return profile

    def _error_response(self, message, status_code):
        return Response({"error": message}, status=status_code)

    @action(detail=False, methods=["get"], permission_classes=[IsOwnerOrAgent])
    def status(self, request):
        """
        Get the verification status of the user.
        """
        profile = get_profile_for_user(request)
        if profile is None:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = VerificationStatusSerializer(profile)
        return Response(
            {
                "status": "success",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsOwnerOrAgent])
    def can_post(self, request):
        """
        Check if the user can post property.
        """
        profile = get_profile_for_user(request)
        if profile is None:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        can_post = profile.can_post_property
        return Response(
            {
                "status": "success",
                "can_post": can_post,
                "reason": (
                    "User is verified" if can_post else "User is not verified"
                ),
            },
            status=status.HTTP_200_OK,
        )


class AdminVerificationViewSet(ListModelMixin, ViewSet):
    """
    Viewset for admin verification management.
    """

    permission_classes = [IsAuthenticated, IsAdmin]     
    pagination_class = PageNumberPagination

    def list(self, request):
        """
        Get the list of verification requests for admin.
        """
        # Get query parameters for filtering
        status_filter = request.query_params.get("status", None)
        role_filter = request.query_params.get("role", None)
        search_query = request.query_params.get("search", None)

        # Get all profiles
        queryset = UserProfile.objects.filter(
            poster_documents__isnull=False,
        ).exclude(poster_documents=[])

        # Apply filters
        if status_filter:
            queryset = queryset.filter(poster_verification_status=status_filter)
        if role_filter:
            queryset = queryset.filter(user__role=role_filter)
        if search_query:
            queryset = queryset.filter(
                Q(user__email__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
            )

        # Order by submission date
        queryset = queryset.order_by("user__date_joined")

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = AdminVerificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AdminVerificationSerializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """
        Approve a verification request.
        """
        profile = get_profile_for_user(request)
        if profile is None:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # check if already verified
        if profile.is_verified_poster:
            return Response(
                {"error": "User already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # update verification status
                profile.is_verified_poster = True
                profile.poster_verification_status = "approved"
                profile.verified_at = timezone.now()
                profile.save()

                return Response(
                    {
                        "status": "success",
                        "message": f"User {profile.user.email} has been verified successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                {
                    "error": "An error occurred while approving the verification request",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Reject a verification request.
        """
        profile = self._get_profile_or_error(request)
        if isinstance(profile, Response):
            return profile

        rejection_reason = request.data.get("reason", "Verification Rejected")
        if not isinstance(rejection_reason, str) or len(rejection_reason) > 100:
            return self._error_response(
                "Rejection reason must be a string up to 255 characters.", status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                profile.poster_verification_status = "rejected"
                profile.verified_at = None
                profile.is_verified_poster = False

                if profile.poster_documents is None:
                    profile.poster_documents = []

                rejection_data = {
                    "id": str(uuid.uuid4()),
                    "type": "rejection",
                    "reason": rejection_reason,
                    "rejected_at": timezone.now().isoformat(),
                    "rejected_by": request.user.email,
                }

                profile.poster_documents.append(rejection_data)
                profile.save()

                return Response(
                    {
                        "status": "success",
                        "message": f"User {profile.user.email} has been rejected successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            import logging
            logging.error(f"Error rejecting verification request for user {getattr(profile.user, 'email', None)}: {e}")
            return self._error_response(
                "An error occurred while rejecting the verification request",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_profile_or_error(self, request):
        profile = get_profile_for_user(request)
        if profile is None:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return profile

    def _error_response(self, message, status_code):
        return Response({"error": message}, status=status_code)
