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
    
    Args:
        user: The user object to determine the serializer for.
        
    Returns:
        The serializer class for the user's role.
    """
    role_serializer_map = {
        "owner": OwnerProfileSerializer,
        "manager": ManagerProfileSerializer,
        "agent": AgentProfileSerializer,
        "tenant": TenantProfileSerializer,
    }
    # Return the specific serializer for the role, or the base UserProfileSerializer if the role is 'user' or not found.
    return role_serializer_map.get(user.role, UserProfileSerializer)

def get_serializer_for_role(role):
    """
    Get serializer for a specific role (useful for admin operations)
    
    Args:
        role: The role to get the serializer for.
        
    Returns:
        The serializer class for the given role.
    """
    role_serializer_map = {
        "owner": OwnerProfileSerializer,
        "manager": ManagerProfileSerializer,
        "agent": AgentProfileSerializer,
        "tenant": TenantProfileSerializer,
    }
    
    return  role_serializer_map.get(role, UserProfileSerializer)
