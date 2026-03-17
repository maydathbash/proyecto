from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('cooking/', include('cooking.urls')),
    path('cuentas/', include('cuentas.urls')),
    path('interacciones/', include('interacciones.urls')),
]