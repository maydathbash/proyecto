from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Avg, Count

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


def _render_valoracion_showcooking_partial(request, showcooking, form=None, status=None, feedback=None, feedback_kind='success'):
	rating_data = showcooking.valoraciones.aggregate(avg=Avg('puntuacion'), total=Count('id'))
	_es_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
	valoraciones_qs = ValoracionShowcooking.objects.filter(showcooking=showcooking).select_related('usuario').order_by('-fecha_creacion')
	if not _es_admin:
		valoraciones_qs = valoraciones_qs.filter(oculto=False)
	valoraciones = valoraciones_qs
	existing = ValoracionShowcooking.objects.filter(usuario=request.user, showcooking=showcooking).first()
	if form is None:
		form = ValoracionShowcookingForm(instance=existing)
	valoracion_usuario_puntuacion = None
	if form.is_bound:
		try:
			valoracion_usuario_puntuacion = int(form.data.get('puntuacion') or 0) or None
		except (TypeError, ValueError):
			valoracion_usuario_puntuacion = None
	elif existing:
		valoracion_usuario_puntuacion = existing.puntuacion

	return render(
		request,
		'interacciones/partials/opiniones_showcooking.html',
		{
			'showcooking': showcooking,
			'valoracion_form': form,
			'valoraciones': valoraciones,
			'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
			'num_valoraciones': rating_data.get('total') or 0,
			'feedback_message': feedback,
			'feedback_kind': feedback_kind,
			'es_admin': _es_admin,
		},
		status=status,
	)


def _render_valoracion_receta_partial(request, receta, form=None, status=None, feedback=None, feedback_kind='success'):
	_es_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
	valoraciones_qs = ValoracionReceta.objects.filter(receta=receta).select_related('usuario').order_by('-id')
	if not _es_admin:
		valoraciones_qs = valoraciones_qs.filter(oculto=False)
	valoraciones = valoraciones_qs
	existing = ValoracionReceta.objects.filter(usuario=request.user, receta=receta).first()
	if form is None:
		form = ValoracionRecetaForm(instance=existing)
	valoracion_usuario_puntuacion = None
	if form.is_bound:
		try:
			valoracion_usuario_puntuacion = int(form.data.get('puntuacion') or 0) or None
		except (TypeError, ValueError):
			valoracion_usuario_puntuacion = None
	elif existing:
		valoracion_usuario_puntuacion = existing.puntuacion

	return render(
		request,
		'interacciones/partials/opiniones_receta.html',
		{
			'receta': receta,
			'valoracion_form': form,
			'valoraciones': valoraciones,
			'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
			'num_valoraciones': valoraciones.count(),
			'feedback_message': feedback,
			'feedback_kind': feedback_kind,
			'es_admin': _es_admin,
		},
		status=status,
	)


@login_required(login_url='login')
def toggle_favorito_showcooking(request, pk):
	showcooking = get_object_or_404(Showcooking, pk=pk)
	favorito = Favorito_showcooking.objects.filter(usuario=request.user, showcooking=showcooking).first()

	if favorito:
		favorito.delete()
	else:
		Favorito_showcooking.objects.create(usuario=request.user, showcooking=showcooking)

	if request.headers.get('HX-Request'):
		is_favorite = Favorito_showcooking.objects.filter(usuario=request.user, showcooking=showcooking).exists()
		return render(request, 'interacciones/partials/favorito_showcooking.html', {
			'showcooking': showcooking,
			'is_favorite': is_favorite,
		})

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
		if request.headers.get('HX-Request'):
			return _render_valoracion_showcooking_partial(
				request,
				showcooking,
				form=form,
				status=422,
				feedback='Revisa la puntuacion y el comentario antes de publicar.',
				feedback_kind='error',
			)
		messages.error(request, 'No se pudo guardar tu valoracion del showcooking.')
		return _redirect_back(request, fallback_name='detalle_showcooking')

	obj = form.save(commit=False)
	obj.usuario = request.user
	obj.showcooking = showcooking
	obj.save()
	if request.headers.get('HX-Request'):
		return _render_valoracion_showcooking_partial(
			request,
			showcooking,
			feedback='Opinion publicada. La lista se ha actualizado sin recargar la pagina.',
		)
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
		if request.headers.get('HX-Request'):
			return _render_valoracion_receta_partial(
				request,
				receta,
				form=form,
				status=422,
				feedback='Revisa la puntuacion y el comentario antes de publicar.',
				feedback_kind='error',
			)
		messages.error(request, 'No se pudo guardar tu valoracion de la receta.')
		return _redirect_back(request, fallback_name='detalle_receta')

	obj = form.save(commit=False)
	obj.usuario = request.user
	obj.receta = receta
	obj.save()
	if request.headers.get('HX-Request'):
		return _render_valoracion_receta_partial(
			request,
			receta,
			feedback='Opinion publicada. La lista se ha actualizado sin recargar la pagina.',
		)
	messages.success(request, 'Opinion guardada correctamente.')
	return _redirect_back(request, fallback_name='detalle_receta')


def _es_admin(user):
	return user.is_active and (user.is_staff or user.is_superuser)


@user_passes_test(_es_admin, login_url='login')
def admin_ocultar_showcooking(request, pk):
	if request.method != 'POST':
		return redirect('core-index')
	showcooking = get_object_or_404(Showcooking, pk=pk)
	showcooking.oculto = not showcooking.oculto
	showcooking.save(update_fields=['oculto'])
	estado = 'ocultado' if showcooking.oculto else 'visible'
	messages.success(request, f'Showcooking "{showcooking.titulo}" {estado}.')
	return _redirect_back(request, fallback_name='core-index')


@user_passes_test(_es_admin, login_url='login')
def admin_ocultar_receta(request, pk):
	if request.method != 'POST':
		return redirect('core-index')
	receta = get_object_or_404(Receta, pk=pk)
	receta.oculto = not receta.oculto
	receta.save(update_fields=['oculto'])
	estado = 'ocultada' if receta.oculto else 'visible'
	messages.success(request, f'Receta "{receta.titulo}" {estado}.')
	return _redirect_back(request, fallback_name='core-recetas')


@user_passes_test(_es_admin, login_url='login')
def admin_ocultar_opinion_showcooking(request, pk):
	if request.method != 'POST':
		return redirect('core-index')
	valoracion = get_object_or_404(ValoracionShowcooking, pk=pk)
	valoracion.oculto = not valoracion.oculto
	valoracion.save(update_fields=['oculto'])
	if request.headers.get('HX-Request'):
		return _render_valoracion_showcooking_partial(request, valoracion.showcooking)
	return _redirect_back(request, fallback_name='core-index')


@user_passes_test(_es_admin, login_url='login')
def admin_ocultar_opinion_receta(request, pk):
	if request.method != 'POST':
		return redirect('core-index')
	valoracion = get_object_or_404(ValoracionReceta, pk=pk)
	valoracion.oculto = not valoracion.oculto
	valoracion.save(update_fields=['oculto'])
	if request.headers.get('HX-Request'):
		return _render_valoracion_receta_partial(request, valoracion.receta)
	return _redirect_back(request, fallback_name='core-recetas')
