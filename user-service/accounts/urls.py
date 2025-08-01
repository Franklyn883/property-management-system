from django.urls import path, include, re_path
from dj_rest_auth.registration.views import RegisterView,VerifyEmailView,ConfirmEmailView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView,PasswordResetView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import InternalUserDetailView
from .views import Profile

urlpatterns = [
    # dj-rest-auth
    path('auth/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    path("auth/registration", RegisterView.as_view(), name="rest_register"),
    path("auth/login", LoginView.as_view(), name="rest_login"),
    path("auth/logout", LogoutView.as_view(), name="rest_logout"),
    path("auth/user", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"
    ),
     path('auth/verify-email/',
         VerifyEmailView.as_view(), name='rest_verify_email'),
    path('auth/account-confirm-email/',
         VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'^auth/account-confirm-email/(?P<key>[-:\w]+)/$',
         VerifyEmailView.as_view(), name='account_confirm_email'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('auth/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),   
    # internal user detail endpoint
    path(
        "internal/users/<uuid:user_id>",
        InternalUserDetailView.as_view(),
        name="internal_user_detail",
    ),
    # user profile
    path("/profile", Profile.user_profile, name="user_profile"),
    # path("profile/agent")
    # path("profile/owner")
    # path("profile/manager")
    # path("profile/tenant")
    # poster verification view
    # handles users who want to post property and needs verification
    # path("profile/poster/submit-verification")
    # path("profile/poster/status")
    # path("profile/poster/can-post-property")
    # admin user router
    # path("admin/users")
    # path("admin/users/<uuid:user_id>/verify-poster")
    # path("admin/user/<uuid:user_id>/roles")
    # path("admin/user/<uuid:user_id>/")
]
