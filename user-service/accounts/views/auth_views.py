from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView
from .rate_limiting import auth_rate_limit, registration_rate_limit
from .account_security import AccountSecurityManager, require_account_security
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


class RateLimitedLoginView(LoginView):
    """Login view with rate limiting and account security."""

    @auth_rate_limit
    @require_account_security
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        password = request.data.get("password", "")

        # Try to authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Successful login
            AccountSecurityManager.record_successful_login(request, user)
            return super().post(request, *args, **kwargs)
        else:
            # Failed login
            AccountSecurityManager.record_failed_login(request, email)
            return Response(
                {
                    "error": "Invalid credentials",
                    "detail": "Email or password is incorrect",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RateLimitedRegisterView(RegisterView):
    """Registration view with rate limiting."""

    @registration_rate_limit
    @require_account_security
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RateLimitedLogoutView(LogoutView):
    """Logout view with rate limiting and session tracking."""

    @auth_rate_limit
    def post(self, request, *args, **kwargs):
        # Record logout before processing
        if request.user.is_authenticated:
            AccountSecurityManager.record_logout(request, request.user)

        return super().post(request, *args, **kwargs)


class RateLimitedPasswordResetView(PasswordResetView):
    """Password reset view with rate limiting."""

    @registration_rate_limit
    @require_account_security
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
