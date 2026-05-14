from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   path('crear/', views.crear_showcooking, name='crear_showcooking'),
   path('showcooking/<int:pk>/editar/', views.editar_showcooking, name='editar_showcooking'),
   path('crear/<int:pk>/receta/', views.crear_receta_showcooking, name='crear_receta_showcooking'),
   path('receta/<int:pk>/editar/', views.editar_receta, name='editar_receta'),
   path('receta/<int:pk>/', views.detalle_receta, name='detalle_receta'),
   path('showcooking/<int:pk>/', views.detalle_showcooking, name='detalle_showcooking'),
]
