from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/index.html'), name='login'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
]