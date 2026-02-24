from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo_usuario', 'fecha_registro', 'avatar', 'biografia')}),
        
    )
    list_display = UserAdmin.list_display + ('tipo_usuario', 'fecha_registro')
    readonly_fields = ('fecha_registro',)
    ordering = ('username',)
    search_fields = ('username', 'tipo_usuario')
    list_filter = UserAdmin.list_filter + ('tipo_usuario',)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo_usuario', 'avatar', 'biografia', 'email')}),
    )
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('username', 'tipo_usuario', 'fecha_registro', 'avatar')
        return self.readonly_fields
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return True
@admin.register(Chef)
class CustomUserChef(admin.ModelAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('id', 'nombre', 'apellidos', 'avatar')}),
    )
    search_fields=('nombre','apellidos')
    
    