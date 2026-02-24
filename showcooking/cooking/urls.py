from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   path('receta/<int:pk>/', views.detalle_receta, name='detalle_receta'),
   path('showcooking/<int:pk>/', views.detalle_showcooking, name='detalle_showcooking'),
]
