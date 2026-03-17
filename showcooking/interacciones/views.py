from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from cooking.models import Showcooking, Receta
from .forms import (
	ValoracionRecetaForm,
	ValoracionShowcookingForm,
)
from .models import (
	Favorito_showcooking,
	RecetaGuardada,
	ValoracionReceta,
	ValoracionShowcooking,
)


def _redirect_back(request, fallback_name='core-index'):
	next_url = request.POST.get('next') or request.GET.get('next')
	if next_url:
		return redirect(next_url)
	return redirect(reverse(fallback_name))


@login_required(login_url='login')
def toggle_favorito_showcooking(request, pk):
	showcooking = get_object_or_404(Showcooking, pk=pk)
	favorito = Favorito_showcooking.objects.filter(usuario=request.user, showcooking=showcooking).first()

	if favorito:
		favorito.delete()
	else:
		Favorito_showcooking.objects.create(usuario=request.user, showcooking=showcooking)

	return _redirect_back(request)


@login_required(login_url='login')
def toggle_receta_guardada(request, pk):
	receta = get_object_or_404(Receta, pk=pk)
	guardada = RecetaGuardada.objects.filter(usuario=request.user, receta=receta).first()

	if guardada:
		guardada.delete()
	else:
		RecetaGuardada.objects.create(usuario=request.user, receta=receta)

	return _redirect_back(request)


@login_required(login_url='login')
def valorar_showcooking(request, pk):
	showcooking = get_object_or_404(Showcooking, pk=pk)
	if request.method != 'POST':
		return redirect('detalle_showcooking', pk=pk)

	existing = ValoracionShowcooking.objects.filter(usuario=request.user, showcooking=showcooking).first()
	form = ValoracionShowcookingForm(request.POST, instance=existing)
	if not form.is_valid():
		messages.error(request, 'No se pudo guardar tu valoracion del showcooking.')
		return _redirect_back(request, fallback_name='detalle_showcooking')

	obj = form.save(commit=False)
	obj.usuario = request.user
	obj.showcooking = showcooking
	obj.save()
	messages.success(request, 'Opinion guardada correctamente.')
	return _redirect_back(request, fallback_name='detalle_showcooking')


@login_required(login_url='login')
def valorar_receta(request, pk):
	receta = get_object_or_404(Receta, pk=pk)
	if request.method != 'POST':
		return redirect('detalle_receta', pk=pk)

	existing = ValoracionReceta.objects.filter(usuario=request.user, receta=receta).first()
	form = ValoracionRecetaForm(request.POST, instance=existing)
	if not form.is_valid():
		messages.error(request, 'No se pudo guardar tu valoracion de la receta.')
		return _redirect_back(request, fallback_name='detalle_receta')

	obj = form.save(commit=False)
	obj.usuario = request.user
	obj.receta = receta
	obj.save()
	messages.success(request, 'Opinion guardada correctamente.')
	return _redirect_back(request, fallback_name='detalle_receta')
