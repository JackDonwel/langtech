from django.contrib import admin
from .models import User, Role, UserRole, Permission, RolePermission

admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(Permission)
admin.site.register(RolePermission)
