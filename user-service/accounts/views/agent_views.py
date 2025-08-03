from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import uuid

from .models import UserProfile
from .permissions import IsAgent
from .utility import get_profile_for_user
from .agent_serializers import (
    AgentLicenseSerializer,
    AgentAgencySerializer,
    AgentStatsSerializer,
    AgentDocumentSerializer,
)


class AgentLicenseViewSet(ViewSet):
    """
    ViewSet for agent license management.
    """

    permission_classes = [IsAuthenticated, IsAgent]

    def get_license(self, request):
        """Get agent's license information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentLicenseSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update_license(self, request):
        """Update agent's license information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentLicenseSerializer(
            profile, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "License information updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def upload_document(self, request):
        """Upload a license document."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentDocumentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.license_documents is None:
                        profile.license_documents = []

                    document_data = {
                        "id": str(uuid.uuid4()),
                        "uploaded_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }

                    profile.license_documents.append(document_data)
                    profile.save()

                    return Response(
                        {
                            "status": "success",
                            "message": "Document uploaded successfully",
                            "data": document_data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                return Response(
                    {"error": "Failed to upload document"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_license_status(self, request):
        """Get detailed license status."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        stats_serializer = AgentStatsSerializer(profile)

        return Response(
            {
                "status": "success",
                "data": {
                    "license_info": stats_serializer.data,
                    "documents_count": len(profile.license_documents or []),
                    "is_license_valid": profile.license_expiration_date
                    and profile.license_expiration_date > date.today(),
                    "requires_renewal": profile.license_expiration_date
                    and profile.license_expiration_date
                    <= date.today() + timedelta(days=30),
                },
            },
            status=status.HTTP_200_OK,
        )


class AgentAgencyViewSet(ViewSet):
    """
    ViewSet for agent agency information management.
    """

    permission_classes = [IsAuthenticated, IsAgent]

    def get_agency_info(self, request):
        """Get agent's agency information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentAgencySerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update_agency_info(self, request):
        """Update agent's agency information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentAgencySerializer(
            profile, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Agency information updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AgentStatsView(APIView):
    """
    View for agent statistics and analytics.
    """

    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        """Get agent statistics."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get basic stats
        stats_serializer = AgentStatsSerializer(profile)

        # Calculate additional statistics
        today = date.today()
        days_since_verification = None
        if profile.verified_at:
            days_since_verification = (today - profile.verified_at.date()).days

        # License statistics
        license_stats = {
            "has_license": bool(profile.license_id),
            "license_expired": profile.license_expiration_date
            and profile.license_expiration_date <= today,
            "license_expiring_soon": profile.license_expiration_date
            and profile.license_expiration_date <= today + timedelta(days=30),
            "days_until_expiration": stats_serializer.get_days_until_expiration(
                profile
            ),
        }

        # Verification statistics
        verification_stats = {
            "is_verified": profile.is_verified_poster,
            "verification_status": profile.poster_verification_status,
            "days_since_verification": days_since_verification,
            "documents_submitted": len(profile.poster_documents or []),
        }

        # Agency statistics
        agency_stats = {
            "agency_name": profile.agency_name,
            "clients_managed": profile.clients_managed_count,
            "has_agency_info": bool(profile.agency_name),
        }

        return Response(
            {
                "status": "success",
                "data": {
                    "profile": stats_serializer.data,
                    "license_stats": license_stats,
                    "verification_stats": verification_stats,
                    "agency_stats": agency_stats,
                },
            },
            status=status.HTTP_200_OK,
        )
