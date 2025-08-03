from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from ..models import FailedLoginAttempt, UserSession, BlockedIP, SecurityAuditLog
from .security import SecurityAuditMiddleware
import logging
from django.db import models

logger = logging.getLogger('security')


class AccountSecurityManager:
    """
    Manager class for account security operations.
    """
    
    @staticmethod
    def get_client_ip(request):
        """Get the client's real IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def check_ip_blocked(request):
        """Check if the IP is blocked."""
        ip_address = AccountSecurityManager.get_client_ip(request)
        return BlockedIP.is_ip_blocked(ip_address)
    
    @staticmethod
    def check_account_locked(request, email):
        """Check if account is locked due to failed attempts."""
        ip_address = AccountSecurityManager.get_client_ip(request)
        
        # Check IP lockout
        if FailedLoginAttempt.is_ip_locked(ip_address):
            SecurityAuditLog.log_event(
                'account_lockout',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'IP lockout', 'email': email}
            )
            return True, "IP address is temporarily locked due to too many failed attempts"
        
        # Check email lockout
        if FailedLoginAttempt.is_email_locked(email):
            SecurityAuditLog.log_event(
                'account_lockout',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'Email lockout', 'email': email}
            )
            return True, "Account is temporarily locked due to too many failed attempts"
        
        return False, None
    
    @staticmethod
    def record_failed_login(request, email, user=None):
        """Record a failed login attempt."""
        ip_address = AccountSecurityManager.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create failed login attempt record
        FailedLoginAttempt.objects.create(
            user=user,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Log the security event
        SecurityAuditLog.log_event(
            'login_failed',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'email': email}
        )
        
        # Check if this should trigger a lockout
        if FailedLoginAttempt.is_ip_locked(ip_address):
            logger.warning(f"IP {ip_address} locked due to too many failed attempts")
        elif FailedLoginAttempt.is_email_locked(email):
            logger.warning(f"Email {email} locked due to too many failed attempts")
    
    @staticmethod
    def record_successful_login(request, user):
        """Record a successful login."""
        ip_address = AccountSecurityManager.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Log the security event
        SecurityAuditLog.log_event(
            'login_success',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'email': user.email}
        )
        
        # Update user's last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Create or update session record
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.update_or_create(
                session_key=session_key,
                defaults={
                    'user': user,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'is_active': True
                }
            )
    
    @staticmethod
    def record_logout(request, user):
        """Record a logout event."""
        ip_address = AccountSecurityManager.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Log the security event
        SecurityAuditLog.log_event(
            'logout',
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'email': user.email}
        )
        
        # Deactivate session
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(session_key=session_key).update(is_active=False)
    
    @staticmethod
    def block_ip(ip_address, reason, blocked_by=None, duration_hours=24):
        """Block an IP address."""
        blocked_until = timezone.now() + timedelta(hours=duration_hours) if duration_hours else None
        
        blocked_ip, created = BlockedIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'blocked_until': blocked_until,
                'blocked_by': blocked_by
            }
        )
        
        if not created:
            # Update existing block
            blocked_ip.reason = reason
            blocked_ip.blocked_until = blocked_until
            blocked_ip.blocked_by = blocked_by
            blocked_ip.save()
        
        # Log the security event
        SecurityAuditLog.log_event(
            'ip_block',
            user=blocked_by,
            ip_address=ip_address,
            details={
                'reason': reason,
                'duration_hours': duration_hours,
                'blocked_until': blocked_until.isoformat() if blocked_until else None
            }
        )
        
        return blocked_ip
    
    @staticmethod
    def unblock_ip(ip_address, unblocked_by=None):
        """Unblock an IP address."""
        try:
            blocked_ip = BlockedIP.objects.get(ip_address=ip_address)
            blocked_ip.delete()
            
            # Log the security event
            SecurityAuditLog.log_event(
                'admin_action',
                user=unblocked_by,
                ip_address=ip_address,
                details={'action': 'unblock_ip', 'reason': 'Manual unblock'}
            )
            
            return True
        except BlockedIP.DoesNotExist:
            return False
    
    @staticmethod
    def cleanup_old_data():
        """Clean up old security data."""
        # Clean up old failed login attempts (older than 7 days)
        cutoff_date = timezone.now() - timedelta(days=7)
        FailedLoginAttempt.objects.filter(timestamp__lt=cutoff_date).delete()
        
        # Clean up old sessions (older than 30 days)
        UserSession.cleanup_old_sessions(days=30)
        
        # Clean up expired IP blocks
        BlockedIP.cleanup_expired_blocks()
        
        # Clean up old audit logs (older than 90 days)
        cutoff_date = timezone.now() - timedelta(days=90)
        SecurityAuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    @staticmethod
    def get_security_stats():
        """Get security statistics."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        return {
            'failed_logins_24h': FailedLoginAttempt.objects.filter(
                timestamp__gte=last_24h
            ).count(),
            'successful_logins_24h': SecurityAuditLog.objects.filter(
                event_type='login_success',
                timestamp__gte=last_24h
            ).count(),
            'active_sessions': UserSession.objects.filter(is_active=True).count(),
            'blocked_ips': BlockedIP.objects.filter(
                models.Q(is_permanent=True) |
                models.Q(blocked_until__isnull=True) |
                models.Q(blocked_until__gt=now)
            ).count(),
            'security_events_7d': SecurityAuditLog.objects.filter(
                timestamp__gte=last_7d
            ).count(),
        }


def require_account_security(view_func):
    """
    Decorator to check account security before allowing access.
    """
    def wrapper(request, *args, **kwargs):
        # Check if IP is blocked
        if AccountSecurityManager.check_ip_blocked(request):
            return HttpResponseForbidden("Access denied: IP address is blocked")
        
        # For login endpoints, check account lockout
        if 'login' in request.path and request.method == 'POST':
            email = request.data.get('email', '')
            if email:
                is_locked, message = AccountSecurityManager.check_account_locked(request, email)
                if is_locked:
                    return HttpResponseForbidden(message)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper 