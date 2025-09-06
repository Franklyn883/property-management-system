from rest_framework import permissions


class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users.
    """

    def has_permission(self, request, view):
        return request.user.is_verified


class IsOwner(permissions.BasePermission):
    """
    Allows access only to users with the role 'owner'.
    """

    def has_permission(self, request, view):
        return request.user.role == "owner"


class IsAgent(permissions.BasePermission):
    """
    Allows access only to the agent of the object.
    """

    def has_permission(self, request, view):
        return request.user.role == "agent"


class IsTenant(permissions.BasePermission):
    """
    Allows access only to users with the role 'tenant'.
    """

    def has_permission(self, request, view):
        return request.user.role == "tenant"


class IsManager(permissions.BasePermission):
    """
    Allows access only to users with the role 'manager'.
    """

    def has_permission(self, request, view):
        return request.user.role == "manager"


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with the role 'admin'.
    """

    def has_permission(self, request, view):
        return request.user.role == "admin"


class IsVerifiedPoster(permissions.BasePermission):
    """Allow access only to verified posters (owner or agent)"""

    def has_permission(self, request, view):
        return (
            request.user.role in ["owner", "agent"]
            and request.user.profile.is_verified_poster
        )


class IsOwnerOrManager(permissions.BasePermission):
    """Allow access only to owners or managers"""

    def has_permission(self, request, view):
        return request.user.role in ["owner", "manager"]


class IsOwnerOrManagerOrAgent(permissions.BasePermission):
    """Allow access only to owners, managers or agents"""

    def has_permission(self, request, view):
        return request.user.role in ["owner", "manager", "agent"]


class IsOwnerOrAgent(permissions.BasePermission):
    """Allow access only to owners or agents"""

    def has_permission(self, request, view):
        return request.user.role in ["owner", "agent"]
