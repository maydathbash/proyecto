from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('inicio_sesion/', views.inicio_sesion, name='iniciar_sesion'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
]