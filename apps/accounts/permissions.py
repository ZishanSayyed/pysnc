from rest_framework.permissions import BasePermission

class IsManagement(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'management'

class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_platform_admin
    
class IsManagementOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['management', 'teacher']
        )