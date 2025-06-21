from django.urls import path, include
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import InternalUserDetailView

urlpatterns = [
    # dj-rest-auth
    path("auth/registration", RegisterView.as_view(), name="rest_register"),
    path("auth/login", LoginView.as_view(), name="rest_login"),
    path("auth/logout", LogoutView.as_view(), name="rest_logout"),
    path("auth/user", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    
    # internal user detail endpoint
    path("internal/users/<uuid:user_id>", InternalUserDetailView.as_view(), name="internal_user_detail"),
    
    #user profile
    #path("auth/profile",) ,

    
  
]
