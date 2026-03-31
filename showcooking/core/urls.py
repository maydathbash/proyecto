from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.index, name='core-index'),
    path('recetas/', views.recetas, name='core-recetas'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('dashboard-chef/', views.dashboard_chef, name='dashboard_chef'),
]

# ESTO ES ESENCIAL PARA DESARROLLO
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)