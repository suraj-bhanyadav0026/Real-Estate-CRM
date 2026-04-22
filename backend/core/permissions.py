from rest_framework import permissions

class IsAuthenticatedCustom(permissions.IsAuthenticated):
    \"\"\"Custom auth with message.\"\"
    def message(self, request):
        return 'Authentication credentials were not provided or invalid.'

class IsAdminOrManager(permissions.BasePermission):
    \"\"\"Only admins/managers.\"\"
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'manager']

class IsAgentOrHigher(permissions.BasePermission):
    \"\"\"Agents, managers, admins.\"\"
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role != 'pending'  # All active roles

class IsOwnerOrAdmin(permissions.BasePermission):
    \"\"\"Owner or admin/manager.\"\"
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'manager']:
            return True
        return obj.user == request.user  # Assuming obj has user field (leads/deals etc.)

# Global use in settings or views

