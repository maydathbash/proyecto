from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cooking/', views.lista_cookings, name='lista_cookings'),
    path('cooking/<int:id>/', views.detalle_cooking, name='detalle_cooking'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('registro/', views.registro, name='registro'),
]