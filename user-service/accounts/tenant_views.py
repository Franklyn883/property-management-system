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
from .permissions import IsTenant
from .utility import get_profile_for_user
from .tenant_serializers import (
    TenantPreferenceSerializer,
    TenantHistorySerializer,
    TenantRatingSerializer,
    TenantHistoryEntrySerializer,
    TenantRatingEntrySerializer,
)


class TenantPreferenceViewSet(ViewSet):
    """
    ViewSet for tenant rental preferences management.
    """
    
    permission_classes = [IsAuthenticated, IsTenant]
    
    def get_preferences(self, request):
        """Get tenant's rental preferences."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantPreferenceSerializer(profile)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def update_preferences(self, request):
        """Update tenant's rental preferences."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantPreferenceSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Rental preferences updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_preference_suggestions(self, request):
        """Get preference suggestions for tenants."""
        suggestions = {
            "property_types": [
                {"value": "apartment", "label": "Apartment"},
                {"value": "house", "label": "House"},
                {"value": "condo", "label": "Condo"},
                {"value": "townhouse", "label": "Townhouse"},
                {"value": "studio", "label": "Studio"},
                {"value": "loft", "label": "Loft"},
                {"value": "duplex", "label": "Duplex"},
                {"value": "penthouse", "label": "Penthouse"},
                {"value": "villa", "label": "Villa"},
            ],
            "amenities": [
                {"value": "parking_required", "label": "Parking Required"},
                {"value": "pet_friendly", "label": "Pet Friendly"},
                {"value": "furnished", "label": "Furnished"},
                {"value": "utilities_included", "label": "Utilities Included"},
            ],
            "lease_durations": [
                {"value": "monthly", "label": "Monthly"},
                {"value": "6_months", "label": "6 Months"},
                {"value": "12_months", "label": "12 Months"},
                {"value": "24_months", "label": "24 Months"},
            ],
            "popular_locations": [
                "Downtown", "Midtown", "Uptown", "Suburbs", "University Area",
                "Business District", "Residential Area", "Shopping District"
            ]
        }
        
        return Response({
            "status": "success",
            "data": suggestions
        }, status=status.HTTP_200_OK)


class TenantHistoryViewSet(ViewSet):
    """
    ViewSet for tenant rental history management.
    """
    
    permission_classes = [IsAuthenticated, IsTenant]
    
    def get_history(self, request):
        """Get tenant's rental history."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantHistorySerializer(profile)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def add_history_entry(self, request):
        """Add a new rental history entry."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantHistoryEntrySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.rental_history is None:
                        profile.rental_history = []
                    
                    history_entry = {
                        "id": str(uuid.uuid4()),
                        "added_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }
                    
                    profile.rental_history.append(history_entry)
                    profile.save()
                    
                    return Response({
                        "status": "success",
                        "message": "Rental history entry added successfully",
                        "data": history_entry
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add history entry"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_history_stats(self, request):
        """Get rental history statistics."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        history = profile.rental_history or []
        
        # Calculate statistics
        total_entries = len(history)
        total_rent_paid = sum(entry.get('monthly_rent', 0) for entry in history)
        average_rent = total_rent_paid / total_entries if total_entries > 0 else 0
        
        # Duration statistics
        total_duration_days = 0
        for entry in history:
            start_date = entry.get('start_date')
            end_date = entry.get('end_date')
            if start_date and end_date:
                from datetime import datetime
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                total_duration_days += (end - start).days
        
        average_duration_months = total_duration_days / 30 if total_duration_days > 0 else 0
        
        stats = {
            "total_entries": total_entries,
            "total_rent_paid": total_rent_paid,
            "average_rent": round(average_rent, 2),
            "average_duration_months": round(average_duration_months, 1),
            "has_history": total_entries > 0,
        }
        
        return Response({
            "status": "success",
            "data": stats
        }, status=status.HTTP_200_OK)


class TenantRatingViewSet(ViewSet):
    """
    ViewSet for tenant rating system.
    """
    
    permission_classes = [IsAuthenticated, IsTenant]
    
    def get_ratings(self, request):
        """Get tenant's ratings."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantRatingSerializer(profile)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def add_rating(self, request):
        """Add a new rating for the tenant."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TenantRatingEntrySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.tenant_ratings is None:
                        profile.tenant_ratings = []
                    
                    rating_entry = {
                        "id": str(uuid.uuid4()),
                        "added_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }
                    
                    profile.tenant_ratings.append(rating_entry)
                    profile.save()
                    
                    return Response({
                        "status": "success",
                        "message": "Rating added successfully",
                        "data": rating_entry
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add rating"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_rating_breakdown(self, request):
        """Get detailed rating breakdown."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        ratings = profile.tenant_ratings or []
        
        # Calculate rating breakdown
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        category_ratings = {}
        
        for rating in ratings:
            rating_value = rating.get('rating', 0)
            if rating_value in rating_counts:
                rating_counts[rating_value] += 1
            
            # Category breakdown
            categories = rating.get('categories', [])
            for category in categories:
                if category not in category_ratings:
                    category_ratings[category] = []
                category_ratings[category].append(rating_value)
        
        # Calculate category averages
        category_averages = {}
        for category, values in category_ratings.items():
            if values:
                category_averages[category] = round(sum(values) / len(values), 1)
        
        breakdown = {
            "rating_distribution": rating_counts,
            "category_averages": category_averages,
            "total_ratings": len(ratings),
            "average_rating": TenantRatingSerializer().get_average_rating(profile),
        }
        
        return Response({
            "status": "success",
            "data": breakdown
        }, status=status.HTTP_200_OK) 