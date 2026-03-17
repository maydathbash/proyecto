from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
	path('favorito/showcooking/<int:pk>/toggle/', views.toggle_favorito_showcooking, name='toggle-favorito-showcooking'),
	path('guardada/receta/<int:pk>/toggle/', views.toggle_receta_guardada, name='toggle-receta-guardada'),
	path('valorar/showcooking/<int:pk>/', views.valorar_showcooking, name='valorar-showcooking'),
	path('valorar/receta/<int:pk>/', views.valorar_receta, name='valorar-receta'),
]