from .models import (
    UserProfile,
    OwnerProfile,
    ManagerProfile,
    AgentProfile,
    TenantProfile,
)
from .serializers import (
    UserProfileSerializer,
    OwnerProfileSerializer,
    ManagerProfileSerializer,
    AgentProfileSerializer,
    TenantProfileSerializer,
)


def get_profile_for_user(user):
    """
    Determines and returns the profile class based on the user's role.
    If the user is an owner, returns OwnerProfile.
    If the user is a manager, returns ManagerProfile.
    If the user is an agent, returns AgentProfile.
    If the user is a tenant, returns TenantProfile.
    Otherwise, returns UserProfile.
    """
    if user.role == "owner":
        return OwnerProfile
    elif user.role == "manager":
        return ManagerProfile
    elif user.role == "agent":
        return AgentProfile
    elif user.role == "tenant":
        return TenantProfile
    else:
        return UserProfile


def get_serializer_for_user(user):
    role_serializer_map = {
        "owner": OwnerProfileSerializer,
        "manager": ManagerProfileSerializer,
        "agent": AgentProfileSerializer,
        "tenant": TenantProfileSerializer,
    }
    return role_serializer_map.get(user.role, UserProfileSerializer)
