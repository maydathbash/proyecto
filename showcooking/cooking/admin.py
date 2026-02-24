from django.contrib import admin
from .models import *
from django.core.exceptions import PermissionDenied
from django.contrib import messages

class CookingAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'fecha_creacion', 'dificultad','publicado')
    search_fields = ('titulo','fecha_creacion')
    list_filter = ('dificultad', 'categoria', 'publicado')
    ordering = ('titulo', 'categoria')
    def save_model(self, request, obj, form, change):
        if not change: # Si es una creación nueva
            obj.creador = request.user
        
        try:
            super().save_model(request, obj, form, change)
        except PermissionDenied as e:
            # Si el Signal lanza el error, lo mostramos como un mensaje de error en el Admin
            messages.error(request, str(e))
            # Opcional: podrías redirigir o manejar el error aquí si fuera necesario
            raise e

admin.site.register(Showcooking, CookingAdmin)

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'showcooking', 'autor', 'fecha_creacion', 'estado')
    search_fields = ('titulo', 'autor__username', 'showcooking__titulo')
    list_filter = ('estado', 'categoria', 'fecha_creacion')
    ordering = ('titulo', 'fecha_creacion')
@admin.register(categoria_showcooking)
class CategoriaShowAdmin(admin.ModelAdmin):
    list_display=['id', 'nombre']
@admin.register(Chef_ShowCooking)
class ChefShowAdmin(admin.ModelAdmin):
    list_display= ('id_showcooking','id_chef')
@admin.register(Categoria_receta)
class categoriarecetaadmin(admin.ModelAdmin):
    list_display=('nombre','id')
    


