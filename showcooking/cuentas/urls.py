from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import inicio_sesion, RegistroUsuarioView, UsuarioDashboardView, UsuarioPublicoView

urlpatterns = [
    path('login/', views.inicio_sesion, name='login'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('usuario/', UsuarioDashboardView.as_view(), name='usuario-dashboard'),
    path('perfil/<str:username>/', UsuarioPublicoView.as_view(), name='usuario-publico'),
]