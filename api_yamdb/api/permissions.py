from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.auth and request.user.is_staff)
            or (request.auth and request.user.is_admin)
        )


class ReviewCommentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_staff or request.user.is_superuser
        )


class Signup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            (request.user and request.user.is_staff)
            or (request.auth and request.user.is_admin)
        )
