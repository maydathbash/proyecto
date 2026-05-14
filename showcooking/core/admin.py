from django.contrib import admin

from .models import inicios_de_sesion

# Register your models here.
@admin.register(inicios_de_sesion)
class IniciosDeSesionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ip', 'fecha_hora')
    list_filter = ('fecha_hora', 'usuario')
    search_fields = ('usuario__username', 'ip')
    ordering = ('-fecha_hora',)

