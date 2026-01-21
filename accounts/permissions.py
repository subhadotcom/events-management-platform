"""
Permissions for the accounts app.
"""

from rest_framework import permissions
from .models import UserRole


class IsSeekerUser(permissions.BasePermission):
    """Permission to check if user is a Seeker"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserRole.SEEKER
        )


class IsFacilitatorUser(permissions.BasePermission):
    """Permission to check if user is a Facilitator"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserRole.FACILITATOR
        )


class IsEmailVerified(permissions.BasePermission):
    """Permission to check if user's email is verified"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.email_verified
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners to edit"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the owner
        return obj.created_by == request.user
