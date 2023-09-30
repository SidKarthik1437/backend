from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'ADMIN')

class IsStudentUser(BasePermission):
    """
    Allows access only to student users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'STUDENT')
