from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(ValoracionShowcooking)
class ValoracionShowcookingAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'showcooking', 'puntuacion']
    list_filter = ['usuario','puntuacion']
    search_fields = ['usuario__username', 'showcooking__titulo']

@admin.register(ValoracionReceta)
class ValoracionRecetaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'receta', 'puntuacion']
    list_filter = ['usuario','puntuacion']
    search_fields = ['usuario__username', 'receta__titulo']

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'showcooking', 'fecha_agregado']
    list_filter = ['usuario','fecha_agregado']
    search_fields = ['usuario__username', 'showcooking__titulo']
@admin.register(RecetaGuardada)
class RecetaGuardadaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'receta', 'fecha_guardado']
    list_filter = ['fecha_guardado']
    search_fields = ['usuario__username', 'receta__titulo']