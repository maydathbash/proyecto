from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='interacciones_index'),
    path('detalle/<int:id>/', views.detalle_interaccion, name='detalle_interaccion'),
]