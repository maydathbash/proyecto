from django.shortcuts import render, get_object_or_404
from cooking.models import *
from cuentas.models import Chef
from django.db.models import Avg, Count


# Create your views here.
def detalle_receta(request, pk):
    # Busca la receta por ID; si no existe, lanza error 404
    receta = get_object_or_404(Receta, pk=pk)
    return render(request, 'detalle_receta.html', {'receta': receta})
def detalle_showcooking(request, pk):
    showcookin = get_object_or_404(Showcooking, pk=pk)
    chefs = Chef_ShowCooking.objects.filter(id_showcooking=showcookin.id).first()
    recetas= Receta.objects.filter(estado='publicada',
                                   showcooking=showcookin)
    print(chefs)
    return render(request, 'detalle_showcooking.html', {'showcooking': showcookin , 'chef' : chefs, 'recetas': recetas})
