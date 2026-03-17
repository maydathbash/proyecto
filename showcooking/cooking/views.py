import re
from urllib.parse import parse_qs, urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from cooking.models import *
from cuentas.models import Chef
from django.db.models import Avg, Count
from interacciones.models import Favorito_showcooking, RecetaGuardada
from interacciones.forms import (
    ValoracionRecetaForm,
    ValoracionShowcookingForm,
)
from interacciones.models import (
    ValoracionReceta,
    ValoracionShowcooking,
)
from .forms import ShowcookingForm, RecetaShowcookingForm


def _youtube_embed_url(url):
    if not url:
        return None
    val = str(url).strip()
    if not val:
        return None
    if val.startswith('www.'):
        val = f'https://{val}'

    parsed = urlparse(val)
    host = (parsed.netloc or '').lower()
    path = parsed.path or ''

    # Acepta dominios habituales de YouTube.
    is_youtube_host = any(h in host for h in ('youtube.com', 'youtu.be', 'youtube-nocookie.com'))
    if not is_youtube_host:
        return None

    if ('youtube.com' in host or 'youtube-nocookie.com' in host) and '/embed/' in path:
        video_id = path.split('/embed/')[-1].split('/')[0]
        if re.fullmatch(r'[A-Za-z0-9_-]{6,}', video_id or ''):
            return f'https://www.youtube.com/embed/{video_id}?rel=0'
        return None

    video_id = None

    if 'youtu.be' in host:
        video_id = path.strip('/').split('/')[0]
    elif 'youtube.com' in host or 'youtube-nocookie.com' in host:
        parts = [p for p in path.split('/') if p]
        if parts and parts[0] == 'watch':
            video_id = parse_qs(parsed.query).get('v', [None])[0]
        elif parts and parts[0] == 'shorts' and len(parts) > 1:
            video_id = parts[1]
        elif parts and parts[0] == 'live' and len(parts) > 1:
            video_id = parts[1]
        elif parts and parts[0] == 'v' and len(parts) > 1:
            video_id = parts[1]
        else:
            video_id = parse_qs(parsed.query).get('v', [None])[0]

    if not video_id or not re.fullmatch(r'[A-Za-z0-9_-]{6,}', video_id):
        return None

    return f'https://www.youtube.com/embed/{video_id}?rel=0'


def _usuario_tiene_rol_chef(user):
    if not user.is_authenticated:
        return False
    rol = getattr(getattr(user, 'tipo_usuario', None), 'nombre_rol', '') or ''
    return rol.strip().lower() in {'chef', 'cocinero'} or bool(user.is_staff or user.is_superuser)


@login_required(login_url='login')
def crear_showcooking(request):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden crear showcookings.')
        return redirect('usuario-dashboard')

    form = ShowcookingForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        showcooking = form.save()
        chef_asignado = form.cleaned_data['chef']
        Chef_ShowCooking.objects.get_or_create(id_showcooking=showcooking, id_chef=chef_asignado)
        messages.success(request, 'Showcooking creado. Ahora puedes anadir recetas dentro de este showcooking.')
        return redirect('crear_receta_showcooking', pk=showcooking.pk)

    return render(request, 'crear_showcooking.html', {'form': form})


@login_required(login_url='login')
def crear_receta_showcooking(request, pk):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden crear recetas.')
        return redirect('usuario-dashboard')

    showcooking = get_object_or_404(Showcooking, pk=pk)

    form = RecetaShowcookingForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        receta = form.save(commit=False)
        receta.showcooking = showcooking
        receta.autor = request.user
        if receta.estado == 'publicada' and not receta.fecha_publicacion:
            receta.fecha_publicacion = timezone.now()
        receta.save()

        chef_asignado = form.cleaned_data['chef']
        Chef_Recetas.objects.get_or_create(id_chef=chef_asignado, id_receta=receta)
        messages.success(request, 'Receta anadida correctamente al showcooking.')
        return redirect('crear_receta_showcooking', pk=showcooking.pk)

    recetas_del_show = Receta.objects.filter(showcooking=showcooking).order_by('-fecha_creacion')

    return render(request, 'crear_receta_showcooking.html', {
        'showcooking': showcooking,
        'form': form,
        'recetas_del_show': recetas_del_show,
    })


# Create your views here.
def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    rating_data = receta.valoraciones.aggregate(avg=Avg('puntuacion'), total=Count('id'))
    valoraciones = ValoracionReceta.objects.filter(receta=receta).select_related('usuario').order_by('-id')

    is_saved = False
    valoracion_form = ValoracionRecetaForm()
    valoracion_usuario_puntuacion = None
    if request.user.is_authenticated:
        is_saved = RecetaGuardada.objects.filter(usuario=request.user, receta=receta).exists()
        valoracion_usuario = ValoracionReceta.objects.filter(usuario=request.user, receta=receta).first()
        if valoracion_usuario:
            valoracion_form = ValoracionRecetaForm(instance=valoracion_usuario)
            valoracion_usuario_puntuacion = valoracion_usuario.puntuacion

    return render(request, 'detalle_receta.html', {
        'receta': receta,
        'avg_rating': rating_data.get('avg'),
        'num_valoraciones': rating_data.get('total') or 0,
        'is_saved': is_saved,
        'valoracion_form': valoracion_form,
        'valoraciones': valoraciones,
        'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
    })


def detalle_showcooking(request, pk):
    showcookin = get_object_or_404(Showcooking, pk=pk)
    chef_rel = Chef_ShowCooking.objects.select_related('id_chef').filter(id_showcooking=showcookin.id).first()
    recetas = Receta.objects.filter(estado='publicada', showcooking=showcookin)
    rating_data = showcookin.valoraciones.aggregate(avg=Avg('puntuacion'), total=Count('id'))
    valoraciones = ValoracionShowcooking.objects.filter(showcooking=showcookin).select_related('usuario').order_by('-fecha_creacion')

    is_favorite = False
    valoracion_form = ValoracionShowcookingForm()
    valoracion_usuario_puntuacion = None
    if request.user.is_authenticated:
        is_favorite = Favorito_showcooking.objects.filter(usuario=request.user, showcooking=showcookin).exists()
        valoracion_usuario = ValoracionShowcooking.objects.filter(usuario=request.user, showcooking=showcookin).first()
        if valoracion_usuario:
            valoracion_form = ValoracionShowcookingForm(instance=valoracion_usuario)
            valoracion_usuario_puntuacion = valoracion_usuario.puntuacion

    return render(request, 'detalle_showcooking.html', {
        'showcooking': showcookin,
        'chef': chef_rel,
        'recetas': recetas,
        'avg_rating': rating_data.get('avg'),
        'num_valoraciones': rating_data.get('total') or 0,
        'embed_youtube_url': _youtube_embed_url(showcookin.url_youtube),
        'video_url_original': showcookin.url_youtube,
        'is_favorite': is_favorite,
        'valoracion_form': valoracion_form,
        'valoraciones': valoraciones,
        'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
    })
