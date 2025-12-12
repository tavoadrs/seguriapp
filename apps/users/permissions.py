from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol == "ADMIN"
        )

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ["ADMIN", "SUPERVISOR"]
        )

class IsTrabajador(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol == "TRABAJADOR"
        )

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                obj.usuario == request.user or 
                request.user.rol in ["ADMIN", "SUPERVISOR"]
            )
        )





























"""from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin or request.user.is_supervisor
        )

class IsTrabajador(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_trabajador

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user or request.user.is_admin or request.user.is_supervisor"""