from django.urls import path, include
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import InternalUserDetailView

urlpatterns = [
    path("register", RegisterView.as_view(), name="rest_register"),
    path("login", LoginView.as_view(), name="rest_login"),
    path("logout", LogoutView.as_view(), name="rest_logout"),
    path("user", UserDetailsView.as_view(), name="rest_user_details"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    
    # internal user detail endpoint
    path("internal/users/<int:user_id>/", InternalUserDetailView.as_view(), name="internal_user_detail"),
  
]
