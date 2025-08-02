from django.urls import path, include, re_path
from dj_rest_auth.registration.views import (
    VerifyEmailView,
    ConfirmEmailView,
)
from dj_rest_auth.views import (
    UserDetailsView,
    PasswordResetConfirmView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    InternalUserDetailView,
    Profile,
    VerificationViewSet,
    AdminVerificationViewSet,
    AdminUserViewSet,
)
from .auth_views import (
    RateLimitedLoginView,
    RateLimitedRegisterView,
    RateLimitedLogoutView,
    RateLimitedPasswordResetView,
)
from .admin_security_views import (
    AdminSecurityStatsView,
    AdminBlockedIPsView,
    AdminUnblockIPView,
    AdminSecurityAuditView,
    AdminCleanupSecurityDataView,
)
from rest_framework.routers import DefaultRouter

# create router for ViewSets
router = DefaultRouter()
router.register(
    r"profile/verification", VerificationViewSet, basename="verification"
)
router.register(
    r"admin/verifications",
    AdminVerificationViewSet,
    basename="admin-verification",
)
router.register(
    r"admin/users",
    AdminUserViewSet,
    basename="admin-users",
)


urlpatterns = [
    # dj-rest-auth
    path("auth/account-confirm-email/<str:key>/", ConfirmEmailView.as_view()),
    path("auth/registration", RateLimitedRegisterView.as_view(), name="rest_register"),
    path("auth/login", RateLimitedLoginView.as_view(), name="rest_login"),
    path("auth/logout", RateLimitedLogoutView.as_view(), name="rest_logout"),
    path("auth/user", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "auth/verify-email/",
        VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    path(
        "auth/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    re_path(
        r"^auth/account-confirm-email/(?P<key>[-:\w]+)/$",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "auth/password-reset/",
        RateLimitedPasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    path(
        "auth/password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # internal user detail endpoint
    path(
        "internal/users/<uuid:user_id>",
        InternalUserDetailView.as_view(),
        name="internal_user_detail",
    ),
    # user profile
    path("profile", Profile.as_view(), name="user_profile"),
    # admin security endpoints
    path("admin/security/stats", AdminSecurityStatsView.as_view(), name="admin_security_stats"),
    path("admin/security/blocked-ips", AdminBlockedIPsView.as_view(), name="admin_blocked_ips"),
    path("admin/security/unblock-ip/<str:ip_address>", AdminUnblockIPView.as_view(), name="admin_unblock_ip"),
    path("admin/security/audit-logs", AdminSecurityAuditView.as_view(), name="admin_security_audit"),
    path("admin/security/cleanup", AdminCleanupSecurityDataView.as_view(), name="admin_security_cleanup"),
    # include router urls
    path("", include(router.urls)),
]
