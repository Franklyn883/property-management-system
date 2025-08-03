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

from ..models import UserProfile, FailedLoginAttempt, UserSession, BlockedIP, SecurityAuditLog
from ..permissions import IsAdmin
from ..security.account_security import AccountSecurityManager
from ..security.security import SecurityAuditMiddleware


class AdminSecurityStatsView(APIView):
    """Admin view for security statistics."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get security statistics."""
        stats = AccountSecurityManager.get_security_stats()
        
        # Add additional stats
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        stats.update({
            'recent_failed_attempts': FailedLoginAttempt.objects.filter(
                timestamp__gte=last_24h
            ).count(),
            'recent_security_events': SecurityAuditLog.objects.filter(
                timestamp__gte=last_24h
            ).count(),
            'total_blocked_ips': BlockedIP.objects.count(),
            'active_sessions_count': UserSession.objects.filter(is_active=True).count(),
        })
        
        return Response({
            "status": "success",
            "data": stats
        }, status=status.HTTP_200_OK)


class AdminBlockedIPsView(APIView):
    """Admin view for managing blocked IPs."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = PageNumberPagination
    
    def get(self, request):
        """Get list of blocked IPs."""
        blocked_ips = BlockedIP.objects.all().order_by('-blocked_at')
        
        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(blocked_ips, request)
        
        if page is not None:
            data = []
            for blocked_ip in page:
                data.append({
                    'ip_address': blocked_ip.ip_address,
                    'reason': blocked_ip.reason,
                    'blocked_at': blocked_ip.blocked_at,
                    'blocked_until': blocked_ip.blocked_until,
                    'is_permanent': blocked_ip.is_permanent,
                    'blocked_by': blocked_ip.blocked_by.email if blocked_ip.blocked_by else None,
                })
            
            return paginator.get_paginated_response(data)
        
        return Response({
            "status": "success",
            "data": []
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Block an IP address."""
        ip_address = request.data.get('ip_address')
        reason = request.data.get('reason', 'Manual block')
        duration_hours = request.data.get('duration_hours', 24)
        is_permanent = request.data.get('is_permanent', False)
        
        if not ip_address:
            return Response({
                "error": "IP address is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            blocked_ip = AccountSecurityManager.block_ip(
                ip_address=ip_address,
                reason=reason,
                blocked_by=request.user,
                duration_hours=None if is_permanent else duration_hours
            )
            
            return Response({
                "status": "success",
                "message": f"IP {ip_address} has been blocked",
                "data": {
                    'ip_address': blocked_ip.ip_address,
                    'reason': blocked_ip.reason,
                    'blocked_at': blocked_ip.blocked_at,
                    'blocked_until': blocked_ip.blocked_until,
                    'is_permanent': blocked_ip.is_permanent,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": f"Failed to block IP: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUnblockIPView(APIView):
    """Admin view for unblocking IPs."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, ip_address):
        """Unblock an IP address."""
        success = AccountSecurityManager.unblock_ip(
            ip_address=ip_address,
            unblocked_by=request.user
        )
        
        if success:
            return Response({
                "status": "success",
                "message": f"IP {ip_address} has been unblocked"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": f"IP {ip_address} is not blocked"
            }, status=status.HTTP_404_NOT_FOUND)


class AdminSecurityAuditView(APIView):
    """Admin view for security audit logs."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = PageNumberPagination
    
    def get(self, request):
        """Get security audit logs."""
        # Get query parameters
        event_type = request.query_params.get('event_type')
        user_email = request.query_params.get('user_email')
        ip_address = request.query_params.get('ip_address')
        days = int(request.query_params.get('days', 7))
        
        # Filter logs
        cutoff_date = timezone.now() - timedelta(days=days)
        logs = SecurityAuditLog.objects.filter(timestamp__gte=cutoff_date)
        
        if event_type:
            logs = logs.filter(event_type=event_type)
        
        if user_email:
            logs = logs.filter(user__email__icontains=user_email)
        
        if ip_address:
            logs = logs.filter(ip_address=ip_address)
        
        logs = logs.order_by('-timestamp')
        
        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(logs, request)
        
        if page is not None:
            data = []
            for log in page:
                data.append({
                    'id': log.id,
                    'event_type': log.get_event_type_display(),
                    'user_email': log.user.email if log.user else None,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'details': log.details,
                    'timestamp': log.timestamp,
                })
            
            return paginator.get_paginated_response(data)
        
        return Response({
            "status": "success",
            "data": []
        }, status=status.HTTP_200_OK)


class AdminCleanupSecurityDataView(APIView):
    """Admin view for cleaning up old security data."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        """Clean up old security data."""
        try:
            AccountSecurityManager.cleanup_old_data()
            
            return Response({
                "status": "success",
                "message": "Security data cleanup completed"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Cleanup failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 