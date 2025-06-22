from .models import (
    UserProfile
)
from .serializers import (
    UserProfileSerializer,
    OwnerProfileSerializer,
    ManagerProfileSerializer,
    AgentProfileSerializer,
    TenantProfileSerializer,
)


def get_serializer_for_user(user):
    """
    Determines and returns the profile serializer class based on the user's role.
    """
    role_serializer_map = {
        "owner": OwnerProfileSerializer,
        "manager": ManagerProfileSerializer,
        "agent": AgentProfileSerializer,
        "tenant": TenantProfileSerializer,
    }
    # Return the specific serializer for the role, or the base UserProfileSerializer if the role is 'user' or not found.
    return role_serializer_map.get(user.role, UserProfileSerializer)
