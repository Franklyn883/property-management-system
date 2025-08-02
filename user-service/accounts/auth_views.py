from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView
from .rate_limiting import auth_rate_limit, registration_rate_limit


class RateLimitedLoginView(LoginView):
    """Login view with rate limiting."""
    
    @auth_rate_limit
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RateLimitedRegisterView(RegisterView):
    """Registration view with rate limiting."""
    
    @registration_rate_limit
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RateLimitedLogoutView(LogoutView):
    """Logout view with rate limiting."""
    
    @auth_rate_limit
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RateLimitedPasswordResetView(PasswordResetView):
    """Password reset view with rate limiting."""
    
    @registration_rate_limit
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs) 