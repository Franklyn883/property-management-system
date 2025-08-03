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

from .views.main_views import (
    InternalUserDetailView,
    Profile,
    VerificationViewSet,
    AdminVerificationViewSet,
    AdminUserViewSet,
)
from .views.auth_views import (
    RateLimitedLoginView,
    RateLimitedRegisterView,
    RateLimitedLogoutView,
    RateLimitedPasswordResetView,
)
from .views.admin_security_views import (
    AdminSecurityStatsView,
    AdminBlockedIPsView,
    AdminUnblockIPView,
    AdminSecurityAuditView,
    AdminCleanupSecurityDataView,
)
from .views.agent_views import (
    AgentLicenseViewSet,
    AgentAgencyViewSet,
    AgentStatsView,
)
from .views.owner_views import (
    OwnerPropertyViewSet,
    OwnerVerificationViewSet,
    OwnerAnalyticsView,
)
from .views.tenant_views import (
    TenantPreferenceViewSet,
    TenantHistoryViewSet,
    TenantRatingViewSet,
)
from .views.manager_views import (
    ManagerAssignmentViewSet,
    ManagerMaintenanceViewSet,
    ManagerDashboardView,
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
    # agent endpoints
    path("agent/license", AgentLicenseViewSet.as_view({'get': 'get_license', 'put': 'update_license'}), name="agent_license"),
    path("agent/license/upload", AgentLicenseViewSet.as_view({'post': 'upload_document'}), name="agent_upload_document"),
    path("agent/license/status", AgentLicenseViewSet.as_view({'get': 'get_license_status'}), name="agent_license_status"),
    path("agent/agency", AgentAgencyViewSet.as_view({'get': 'get_agency_info', 'put': 'update_agency_info'}), name="agent_agency"),
    path("agent/stats", AgentStatsView.as_view(), name="agent_stats"),
    # owner endpoints
    path("owner/property", OwnerPropertyViewSet.as_view({'get': 'get_property_info', 'put': 'update_property_info'}), name="owner_property"),
    path("owner/property/upload", OwnerPropertyViewSet.as_view({'post': 'upload_document'}), name="owner_upload_document"),
    path("owner/verification", OwnerVerificationViewSet.as_view({'get': 'get_verification_status'}), name="owner_verification"),
    path("owner/verification/requirements", OwnerVerificationViewSet.as_view({'get': 'get_verification_requirements'}), name="owner_verification_requirements"),
    path("owner/analytics", OwnerAnalyticsView.as_view(), name="owner_analytics"),
    # tenant endpoints
    path("tenant/preferences", TenantPreferenceViewSet.as_view({'get': 'get_preferences', 'put': 'update_preferences'}), name="tenant_preferences"),
    path("tenant/preferences/suggestions", TenantPreferenceViewSet.as_view({'get': 'get_preference_suggestions'}), name="tenant_preference_suggestions"),
    path("tenant/history", TenantHistoryViewSet.as_view({'get': 'get_history'}), name="tenant_history"),
    path("tenant/history/add", TenantHistoryViewSet.as_view({'post': 'add_history_entry'}), name="tenant_add_history"),
    path("tenant/history/stats", TenantHistoryViewSet.as_view({'get': 'get_history_stats'}), name="tenant_history_stats"),
    path("tenant/ratings", TenantRatingViewSet.as_view({'get': 'get_ratings'}), name="tenant_ratings"),
    path("tenant/ratings/add", TenantRatingViewSet.as_view({'post': 'add_rating'}), name="tenant_add_rating"),
    path("tenant/ratings/breakdown", TenantRatingViewSet.as_view({'get': 'get_rating_breakdown'}), name="tenant_rating_breakdown"),
    # manager endpoints
    path("manager/assignments", ManagerAssignmentViewSet.as_view({'get': 'get_assignments', 'put': 'update_assignments'}), name="manager_assignments"),
    path("manager/assignments/add", ManagerAssignmentViewSet.as_view({'post': 'add_assignment'}), name="manager_add_assignment"),
    path("manager/assignments/stats", ManagerAssignmentViewSet.as_view({'get': 'get_assignment_stats'}), name="manager_assignment_stats"),
    path("manager/maintenance", ManagerMaintenanceViewSet.as_view({'get': 'get_maintenance_requests'}), name="manager_maintenance"),
    path("manager/maintenance/add", ManagerMaintenanceViewSet.as_view({'post': 'add_maintenance_request'}), name="manager_add_maintenance"),
    path("manager/maintenance/<str:request_id>/status", ManagerMaintenanceViewSet.as_view({'put': 'update_request_status'}), name="manager_update_request_status"),
    path("manager/maintenance/stats", ManagerMaintenanceViewSet.as_view({'get': 'get_maintenance_stats'}), name="manager_maintenance_stats"),
    path("manager/dashboard", ManagerDashboardView.as_view(), name="manager_dashboard"),
    # include router urls
    path("", include(router.urls)),
]
