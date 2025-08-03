from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from django.db import transaction
from django.utils import timezone
import uuid

from .models import UserProfile
from .permissions import IsOwner
from .utility import get_profile_for_user
from .owner_serializers import (
    OwnerPropertySerializer,
    OwnerVerificationSerializer,
    OwnerAnalyticsSerializer,
    OwnerDocumentSerializer,
)


class OwnerPropertyViewSet(ViewSet):
    """
    ViewSet for owner property management.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_property_info(self, request):
        """Get owner's property information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OwnerPropertySerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update_property_info(self, request):
        """Update owner's property information."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OwnerPropertySerializer(
            profile, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Property information updated successfully",
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
        """Upload an ownership document."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OwnerDocumentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.ownership_documents is None:
                        profile.ownership_documents = []

                    document_data = {
                        "id": str(uuid.uuid4()),
                        "uploaded_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }

                    profile.ownership_documents.append(document_data)
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


class OwnerVerificationViewSet(ViewSet):
    """
    ViewSet for owner verification management.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_verification_status(self, request):
        """Get owner's verification status."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OwnerVerificationSerializer(profile)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def get_verification_requirements(self, request):
        """Get verification requirements for owners."""
        requirements = {
            "documents_required": [
                {
                    "type": "deed",
                    "name": "Property Deed",
                    "description": "Official property deed showing ownership",
                    "required": True,
                },
                {
                    "type": "title",
                    "name": "Property Title",
                    "description": "Property title document",
                    "required": True,
                },
                {
                    "type": "tax_assessment",
                    "name": "Tax Assessment",
                    "description": "Current property tax assessment",
                    "required": False,
                },
                {
                    "type": "insurance",
                    "name": "Property Insurance",
                    "description": "Property insurance certificate",
                    "required": False,
                },
            ],
            "verification_process": [
                "Upload required ownership documents",
                "Submit verification request",
                "Wait for admin review (1-3 business days)",
                "Receive verification status update",
            ],
            "benefits": [
                "Post property listings",
                "Access to premium features",
                "Verified owner badge",
                "Priority customer support",
            ],
        }

        return Response(
            {"status": "success", "data": requirements},
            status=status.HTTP_200_OK,
        )


class OwnerAnalyticsView(APIView):
    """
    View for owner analytics and insights.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        """Get owner analytics."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get basic analytics
        analytics_serializer = OwnerAnalyticsSerializer(profile)

        # Calculate additional analytics
        documents_count = len(profile.ownership_documents or [])
        verification_days = analytics_serializer.get_days_since_verification(
            profile
        )

        # Property analytics
        property_stats = {
            "total_properties": profile.properties_owned_count,
            "has_properties": profile.properties_owned_count > 0,
            "property_range": self._get_property_range(
                profile.properties_owned_count
            ),
        }

        # Document analytics
        document_stats = {
            "total_documents": documents_count,
            "has_documents": documents_count > 0,
            "document_types": self._get_document_types(
                profile.ownership_documents
            ),
            "completion_percentage": self._calculate_completion_percentage(
                documents_count
            ),
        }

        # Verification analytics
        verification_stats = {
            "is_verified": profile.is_verified_poster,
            "verification_status": profile.poster_verification_status,
            "days_since_verification": verification_days,
            "verification_age": self._get_verification_age(verification_days),
        }

        return Response(
            {
                "status": "success",
                "data": {
                    "profile": analytics_serializer.data,
                    "property_stats": property_stats,
                    "document_stats": document_stats,
                    "verification_stats": verification_stats,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _get_property_range(self, count):
        """Get property count range."""
        if count == 0:
            return "no_properties"
        elif count == 1:
            return "single_property"
        elif count <= 5:
            return "small_portfolio"
        elif count <= 20:
            return "medium_portfolio"
        else:
            return "large_portfolio"

    def _get_document_types(self, documents):
        """Get document types from ownership documents."""
        if not documents:
            return []

        types = []
        for doc in documents:
            doc_type = doc.get("type", "unknown")
            if doc_type not in types:
                types.append(doc_type)

        return types

    def _calculate_completion_percentage(self, documents_count):
        """Calculate document completion percentage."""
        required_docs = 2  # deed and title
        if documents_count >= required_docs:
            return 100
        else:
            return int((documents_count / required_docs) * 100)

    def _get_verification_age(self, days):
        """Get verification age category."""
        if days is None:
            return "not_verified"
        elif days <= 30:
            return "recent"
        elif days <= 90:
            return "medium"
        else:
            return "established"
