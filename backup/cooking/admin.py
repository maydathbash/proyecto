from django.contrib import admin
from .models import *

class CookingAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'fecha_creacion', 'dificultad','publicado')
    search_fields = ('titulo','fecha_creacion')
    list_filter = ('dificultad', 'categoria', 'publicado')
    ordering = ('titulo', 'categoria')

admin.site.register(Showcooking, CookingAdmin, categoria_showcooking, Categoria_receta, Chef_ShowCooking, Chef_Recetas, ingredientes_receta)

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'showcooking', 'autor', 'fecha_creacion', 'estado')
    search_fields = ('titulo', 'autor__username', 'showcooking__titulo')
    list_filter = ('estado', 'categoria', 'fecha_creacion')
    ordering = ('titulo', 'fecha_creacion')
@admin.register(ingredientes)
class IngredientesAdmin(admin.ModelAdmin):
    list_display=('id', 'nombre')
    search_fields = ('nombre')



