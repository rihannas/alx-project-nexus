from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow full access if admin, read-only otherwise.
    """
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser) or request.method in permissions.SAFE_METHODS)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission: Only owners or admins can access objects.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True

        # For User object itself
        if hasattr(obj, 'id') and obj.id == request.user.id:
            return True

        # For related objects with user attribute
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # For CartItem or OrderItem that belongs to a user's cart/order
        if hasattr(obj, 'cart') and obj.cart.user == request.user:
            return True

        if hasattr(obj, 'order') and obj.order.user == request.user:
            return True

        return False
