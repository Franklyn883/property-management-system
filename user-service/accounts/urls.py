from django.urls import path, include
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import InternalUserDetailView, user_profile

urlpatterns = [
    # dj-rest-auth
    path("auth/registration", RegisterView.as_view(), name="rest_register"),
    path("auth/login", LoginView.as_view(), name="rest_login"),
    path("auth/logout", LogoutView.as_view(), name="rest_logout"),
    path("auth/user", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"
    ),
    # internal user detail endpoint
    path(
        "internal/users/<uuid:user_id>",
        InternalUserDetailView.as_view(),
        name="internal_user_detail",
    ),
    # user profile
    path("auth/profile", user_profile, name="user_profile"),
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
