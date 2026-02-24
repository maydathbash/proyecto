from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.index, name='core-index'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
]