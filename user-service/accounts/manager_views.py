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
from .permissions import IsManager
from .utility import get_profile_for_user
from .manager_serializers import (
    ManagerAssignmentSerializer,
    ManagerMaintenanceSerializer,
    ManagerDashboardSerializer,
    ManagerAssignmentEntrySerializer,
    ManagerMaintenanceEntrySerializer,
    ManagerContractEntrySerializer,
)


class ManagerAssignmentViewSet(ViewSet):
    """
    ViewSet for manager property assignment management.
    """
    
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_assignments(self, request):
        """Get manager's property assignments."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ManagerAssignmentSerializer(profile)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def update_assignments(self, request):
        """Update manager's property assignments."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ManagerAssignmentSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Property assignments updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def add_assignment(self, request):
        """Add a new property assignment."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ManagerAssignmentEntrySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.assigned_properties is None:
                        profile.assigned_properties = []
                    
                    assignment_data = {
                        "id": str(uuid.uuid4()),
                        "added_at": timezone.now().isoformat(),
                        **serializer.validated_data,
                    }
                    
                    profile.assigned_properties.append(assignment_data)
                    profile.save()
                    
                    return Response({
                        "status": "success",
                        "message": "Property assignment added successfully",
                        "data": assignment_data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add property assignment"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_assignment_stats(self, request):
        """Get assignment statistics."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        assignments = profile.assigned_properties or []
        contracts = profile.management_contracts or []
        
        # Calculate statistics
        total_assignments = len(assignments)
        total_contracts = len(contracts)
        active_assignments = sum(1 for assignment in assignments if assignment.get('status') != 'terminated')
        
        # Calculate total management fees
        total_fees = sum(assignment.get('management_fee', 0) for assignment in assignments)
        
        stats = {
            "total_assignments": total_assignments,
            "active_assignments": active_assignments,
            "total_contracts": total_contracts,
            "total_management_fees": total_fees,
            "average_fee": round(total_fees / total_assignments, 2) if total_assignments > 0 else 0,
        }
        
        return Response({
            "status": "success",
            "data": stats
        }, status=status.HTTP_200_OK)


class ManagerMaintenanceViewSet(ViewSet):
    """
    ViewSet for manager maintenance request management.
    """
    
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_maintenance_requests(self, request):
        """Get manager's maintenance requests."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ManagerMaintenanceSerializer(profile)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def add_maintenance_request(self, request):
        """Add a new maintenance request."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ManagerMaintenanceEntrySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    if profile.maintenance_requests is None:
                        profile.maintenance_requests = []
                    
                    request_data = {
                        "id": str(uuid.uuid4()),
                        "created_at": timezone.now().isoformat(),
                        "status": "pending",
                        **serializer.validated_data,
                    }
                    
                    profile.maintenance_requests.append(request_data)
                    profile.save()
                    
                    return Response({
                        "status": "success",
                        "message": "Maintenance request added successfully",
                        "data": request_data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add maintenance request"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update_request_status(self, request, request_id):
        """Update maintenance request status."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        requests = profile.maintenance_requests or []
        request_found = False
        
        for req in requests:
            if req.get('id') == request_id:
                req['status'] = request.data.get('status', req.get('status'))
                req['updated_at'] = timezone.now().isoformat()
                if 'notes' in request.data:
                    req['notes'] = request.data['notes']
                request_found = True
                break
        
        if not request_found:
            return Response({
                "error": "Maintenance request not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        profile.save()
        
        return Response({
            "status": "success",
            "message": "Maintenance request status updated successfully"
        }, status=status.HTTP_200_OK)
    
    def get_maintenance_stats(self, request):
        """Get maintenance request statistics."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        requests = profile.maintenance_requests or []
        
        # Calculate statistics
        total_requests = len(requests)
        pending_requests = sum(1 for req in requests if req.get('status') == 'pending')
        in_progress_requests = sum(1 for req in requests if req.get('status') == 'in_progress')
        completed_requests = sum(1 for req in requests if req.get('status') == 'completed')
        
        # Calculate total estimated costs
        total_estimated_cost = sum(req.get('estimated_cost', 0) for req in requests)
        
        # Priority breakdown
        priority_counts = {
            'low': sum(1 for req in requests if req.get('priority') == 'low'),
            'medium': sum(1 for req in requests if req.get('priority') == 'medium'),
            'high': sum(1 for req in requests if req.get('priority') == 'high'),
            'urgent': sum(1 for req in requests if req.get('priority') == 'urgent'),
        }
        
        stats = {
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "in_progress_requests": in_progress_requests,
            "completed_requests": completed_requests,
            "total_estimated_cost": total_estimated_cost,
            "priority_breakdown": priority_counts,
        }
        
        return Response({
            "status": "success",
            "data": stats
        }, status=status.HTTP_200_OK)


class ManagerDashboardView(APIView):
    """
    View for manager dashboard and analytics.
    """
    
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        """Get manager dashboard data."""
        profile = get_profile_for_user(request)
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        # Get basic dashboard data
        dashboard_serializer = ManagerDashboardSerializer(profile)
        
        # Calculate additional analytics
        assignments = profile.assigned_properties or []
        contracts = profile.management_contracts or []
        requests = profile.maintenance_requests or []
        
        # Property analytics
        property_stats = {
            "total_properties": len(assignments),
            "active_properties": sum(1 for assignment in assignments if assignment.get('status') != 'terminated'),
            "properties_by_status": self._get_property_status_breakdown(assignments),
        }
        
        # Contract analytics
        contract_stats = {
            "total_contracts": len(contracts),
            "active_contracts": sum(1 for contract in contracts if contract.get('status') != 'expired'),
            "total_commission": sum(contract.get('commission_rate', 0) for contract in contracts),
            "average_commission": self._calculate_average_commission(contracts),
        }
        
        # Maintenance analytics
        maintenance_stats = {
            "total_requests": len(requests),
            "active_requests": sum(1 for req in requests if req.get('status') in ['pending', 'in_progress']),
            "urgent_requests": sum(1 for req in requests if req.get('priority') == 'urgent'),
            "total_estimated_cost": sum(req.get('estimated_cost', 0) for req in requests),
        }
        
        # Performance metrics
        performance_metrics = {
            "response_time_avg": self._calculate_avg_response_time(requests),
            "completion_rate": self._calculate_completion_rate(requests),
            "customer_satisfaction": self._calculate_satisfaction_score(requests),
        }
        
        return Response({
            "status": "success",
            "data": {
                "profile": dashboard_serializer.data,
                "property_stats": property_stats,
                "contract_stats": contract_stats,
                "maintenance_stats": maintenance_stats,
                "performance_metrics": performance_metrics,
            }
        }, status=status.HTTP_200_OK)
    
    def _get_property_status_breakdown(self, assignments):
        """Get property status breakdown."""
        status_counts = {}
        for assignment in assignments:
            status = assignment.get('status', 'active')
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _calculate_average_commission(self, contracts):
        """Calculate average commission rate."""
        if not contracts:
            return 0
        total_commission = sum(contract.get('commission_rate', 0) for contract in contracts)
        return round(total_commission / len(contracts), 2)
    
    def _calculate_avg_response_time(self, requests):
        """Calculate average response time for maintenance requests."""
        # This would typically involve more complex date calculations
        # For now, return a placeholder
        return "24 hours"
    
    def _calculate_completion_rate(self, requests):
        """Calculate completion rate for maintenance requests."""
        if not requests:
            return 0
        completed = sum(1 for req in requests if req.get('status') == 'completed')
        return round((completed / len(requests)) * 100, 1)
    
    def _calculate_satisfaction_score(self, requests):
        """Calculate customer satisfaction score."""
        # This would typically involve rating calculations
        # For now, return a placeholder
        return 4.2 