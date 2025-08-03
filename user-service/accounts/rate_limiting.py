from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def api_rate_limit(key="ip", rate="5/m", method="GET", block=True):
    """
    Decorator for API rate limiting with custom configuration.

    Args:
        key: Rate limit key ('ip', 'user', 'post', etc.)
        rate: Rate limit (e.g., '5/m', '100/h', '1000/d')
        method: HTTP method to apply rate limiting to
        block: Whether to block requests when limit exceeded
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            # Apply rate limiting
            @ratelimit(key=key, rate=rate, method=method, block=block)
            def rate_limited_view(request, *args, **kwargs):
                return view_func(self, request, *args, **kwargs)

            try:
                return rate_limited_view(request, *args, **kwargs)
            except Ratelimited:
                return Response(
                    {
                        "error": "Rate limit exceeded",
                        "detail": f"Too many requests. Limit: {rate}",
                        "retry_after": 60,  # Retry after 1 minute
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        return wrapped_view

    return decorator


# Predefined rate limit configurations
def auth_rate_limit(view_func):
    """Rate limit for authentication endpoints (5 requests per minute)"""
    return api_rate_limit(key="ip", rate="5/m", method="POST")(view_func)


def registration_rate_limit(view_func):
    """Rate limit for registration endpoints (3 requests per hour)"""
    return api_rate_limit(key="ip", rate="3/h", method="POST")(view_func)


def admin_rate_limit(view_func):
    """Rate limit for admin endpoints (20 requests per minute)"""
    return api_rate_limit(key="user", rate="20/m", method="GET")(view_func)


def profile_rate_limit(view_func):
    """Rate limit for profile update endpoints (10 requests per minute)"""
    return api_rate_limit(key="user", rate="10/m", method="PUT")(view_func)


def verification_rate_limit(view_func):
    """Rate limit for verification endpoints (3 requests per hour)"""
    return api_rate_limit(key="user", rate="3/h", method="POST")(view_func)


def general_api_rate_limit(view_func):
    """General rate limit for API endpoints (100 requests per hour)"""
    return api_rate_limit(key="ip", rate="100/h", method="GET")(view_func)
