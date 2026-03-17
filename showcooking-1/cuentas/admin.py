from django.contrib import admin
from .models import User, Chef, Role  # Assuming these are the models defined in cuentas/models.py

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'email')

class ChefAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'specialty')
    search_fields = ('name',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(Chef, ChefAdmin)
admin.site.register(Role, RoleAdmin)