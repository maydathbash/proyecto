import re
from urllib.parse import parse_qs, urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from cooking.models import *
from cuentas.models import Chef
from django.db.models import Avg, Count, F
from interacciones.models import Favorito_showcooking, RecetaGuardada
from interacciones.forms import (
    ValoracionRecetaForm,
    ValoracionShowcookingForm,
)
from interacciones.models import (
    ValoracionReceta,
    ValoracionShowcooking,
)
from .forms import ShowcookingForm, RecetaShowcookingForm, IngredienteRecetaFormSet


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


def _obtener_chef_actual(user):
    nombre_chef = (user.first_name or user.username or '').strip()
    apellidos_chef = (user.last_name or '').strip()

    if not nombre_chef:
        return None

    chef_actual = Chef.objects.filter(
        nombre__iexact=nombre_chef,
        apellidos__iexact=apellidos_chef,
    ).first()
    if chef_actual is None:
        chef_actual = Chef.objects.create(nombre=nombre_chef[:30], apellidos=apellidos_chef[:80])
    return chef_actual


def _obtener_usuario_de_chef(chef):
    if not chef:
        return None
    return chef.usuario_vinculado


def _obtener_datos_avatar_chef(chef):
    usuario = _obtener_usuario_de_chef(chef)

    if usuario and getattr(usuario, 'avatar', None):
        try:
            return usuario.avatar.url, usuario.avatar_initial
        except Exception:
            pass

    if chef:
        avatar_visible = getattr(chef, 'url_avatar_visible', None)
        if avatar_visible:
            return avatar_visible, chef.inicial_visible

    fuente_inicial = None
    if usuario:
        fuente_inicial = getattr(usuario, 'avatar_initial', None) or getattr(usuario, 'username', None)
    if not fuente_inicial and chef:
        fuente_inicial = chef.nombre or str(chef)

    inicial = (fuente_inicial or 'S')[:1].upper()
    return None, inicial


def _estrellas_valoracion_media(valoracion_media):
    if not valoracion_media:
        return None

    puntuacion_redondeada = max(0, min(5, round(valoracion_media)))
    return ('★' * puntuacion_redondeada) + ('☆' * (5 - puntuacion_redondeada))


@login_required(login_url='login')
def crear_showcooking(request):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden crear showcookings.')
        return redirect('usuario-dashboard')

    chef_actual = _obtener_chef_actual(request.user)

    if chef_actual is None:
        messages.error(request, 'No se pudo preparar tu perfil de chef para crear el showcooking.')
        return redirect('usuario-dashboard')

    form = ShowcookingForm(request.POST or None, request.FILES or None, chef_fijado=chef_actual)

    if request.method == 'POST' and form.is_valid():
        showcooking = form.save()
        chef_asignado = form.cleaned_data['chef']
        Chef_ShowCooking.objects.get_or_create(id_showcooking=showcooking, id_chef=chef_asignado)
        messages.success(request, 'Showcooking creado. Ahora puedes anadir recetas dentro de este showcooking.')
        return redirect('crear_receta_showcooking', pk=showcooking.pk)

    return render(request, 'crear_showcooking.html', {'form': form})


@login_required(login_url='login')
def editar_showcooking(request, pk):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden modificar showcookings.')
        return redirect('usuario-dashboard')

    showcooking = get_object_or_404(Showcooking, pk=pk)
    chef_actual = _obtener_chef_actual(request.user)
    relacion_chef = Chef_ShowCooking.objects.filter(id_showcooking=showcooking).select_related('id_chef').first()

    if chef_actual is None or relacion_chef is None or relacion_chef.id_chef_id != chef_actual.id:
        messages.error(request, 'Solo puedes modificar showcookings creados por ti.')
        return redirect('dashboard_chef')

    form = ShowcookingForm(
        request.POST or None,
        request.FILES or None,
        instance=showcooking,
        chef_fijado=chef_actual,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Showcooking actualizado correctamente.')
        return redirect('dashboard_chef')

    return render(request, 'crear_showcooking.html', {
        'form': form,
        'showcooking': showcooking,
        'modo_edicion': True,
    })


@login_required(login_url='login')
def crear_receta_showcooking(request, pk):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden crear recetas.')
        return redirect('usuario-dashboard')

    showcooking = get_object_or_404(Showcooking, pk=pk)
    chef_actual = _obtener_chef_actual(request.user)

    form = RecetaShowcookingForm(
        request.POST or None,
        request.FILES or None,
        chef_inicial=chef_actual,
    )
    receta_borrador = Receta(showcooking=showcooking, autor=request.user)
    ingredient_formset = IngredienteRecetaFormSet(
        request.POST or None,
        instance=receta_borrador,
        prefix='ingredientes',
    )

    if request.method == 'POST' and form.is_valid() and ingredient_formset.is_valid():
        receta = form.save(commit=False)
        receta.showcooking = showcooking
        receta.autor = request.user
        if receta.estado == 'publicada' and not receta.fecha_publicacion:
            receta.fecha_publicacion = timezone.now()
        receta.save()
        ingredient_formset.instance = receta
        ingredient_formset.save()

        chef_asignado = form.cleaned_data['chef']
        Chef_Recetas.objects.get_or_create(id_chef=chef_asignado, id_receta=receta)
        messages.success(request, 'Receta anadida correctamente al showcooking.')
        return redirect('crear_receta_showcooking', pk=showcooking.pk)

    recetas_del_show = Receta.objects.filter(showcooking=showcooking).order_by('-fecha_creacion')

    return render(request, 'crear_receta_showcooking.html', {
        'showcooking': showcooking,
        'form': form,
        'ingredient_formset': ingredient_formset,
        'recetas_del_show': recetas_del_show,
    })


@login_required(login_url='login')
def editar_receta(request, pk):
    if not _usuario_tiene_rol_chef(request.user):
        messages.error(request, 'Solo usuarios con rol Chef pueden modificar recetas.')
        return redirect('usuario-dashboard')

    receta = get_object_or_404(Receta, pk=pk)
    if receta.autor_id != request.user.id:
        messages.error(request, 'Solo puedes modificar recetas creadas por ti.')
        return redirect('dashboard_chef')

    chef_actual = _obtener_chef_actual(request.user)
    relacion_chef = Chef_Recetas.objects.filter(id_receta=receta).select_related('id_chef').first()

    form = RecetaShowcookingForm(
        request.POST or None,
        request.FILES or None,
        instance=receta,
        chef_inicial=relacion_chef.id_chef if relacion_chef else chef_actual,
    )
    ingredient_formset = IngredienteRecetaFormSet(
        request.POST or None,
        instance=receta,
        prefix='ingredientes',
    )

    if request.method == 'POST' and form.is_valid() and ingredient_formset.is_valid():
        receta_actualizada = form.save(commit=False)
        receta_actualizada.showcooking = receta.showcooking
        receta_actualizada.autor = receta.autor
        if receta_actualizada.estado == 'publicada' and not receta_actualizada.fecha_publicacion:
            receta_actualizada.fecha_publicacion = timezone.now()
        receta_actualizada.save()
        ingredient_formset.instance = receta_actualizada
        ingredient_formset.save()

        chef_asignado = form.cleaned_data['chef']
        if chef_asignado:
            Chef_Recetas.objects.update_or_create(
                id_receta=receta_actualizada,
                defaults={'id_chef': chef_asignado},
            )

        messages.success(request, 'Receta actualizada correctamente.')
        return redirect('detalle_receta', pk=receta_actualizada.pk)

    recetas_del_show = Receta.objects.filter(showcooking=receta.showcooking).order_by('-fecha_creacion')

    return render(request, 'crear_receta_showcooking.html', {
        'showcooking': receta.showcooking,
        'form': form,
        'ingredient_formset': ingredient_formset,
        'recetas_del_show': recetas_del_show,
        'modo_edicion': True,
        'receta': receta,
    })


# Create your views here.
def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    Receta.objects.filter(pk=receta.pk).update(visitas=F('visitas') + 1)
    receta.refresh_from_db(fields=['visitas'])
    rating_data = receta.valoraciones.aggregate(avg=Avg('puntuacion'), total=Count('id'))
    avg_rating = rating_data.get('avg')
    _es_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    valoraciones_qs = ValoracionReceta.objects.filter(receta=receta).select_related('usuario').order_by('-id')
    if not _es_admin:
        valoraciones_qs = valoraciones_qs.filter(oculto=False)
    valoraciones = valoraciones_qs

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
        'avg_rating': avg_rating,
        'avg_rating_stars': _estrellas_valoracion_media(avg_rating),
        'num_valoraciones': rating_data.get('total') or 0,
        'is_saved': is_saved,
        'valoracion_form': valoracion_form,
        'valoraciones': valoraciones,
        'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
        'es_admin': _es_admin,
    })


def detalle_showcooking(request, pk):
    showcookin = get_object_or_404(Showcooking, pk=pk)
    chef_rel = Chef_ShowCooking.objects.select_related('id_chef').filter(id_showcooking=showcookin.id).first()
    chef_obj = chef_rel.id_chef if chef_rel else None
    usuario_chef = chef_obj.usuario_vinculado if chef_obj else None

    if not request.user.is_authenticated or not usuario_chef or request.user.pk != usuario_chef.pk:
        Showcooking.objects.filter(pk=showcookin.pk).update(visitas=F('visitas') + 1)
        showcookin.refresh_from_db(fields=['visitas'])

    url_avatar_chef, inicial_avatar_chef = _obtener_datos_avatar_chef(chef_obj)
    url_perfil_chef = chef_obj.url_perfil_publico if chef_obj else None
    recetas = Receta.objects.filter(estado='publicada', showcooking=showcookin)
    rating_data = showcookin.valoraciones.aggregate(avg=Avg('puntuacion'), total=Count('id'))
    avg_rating = rating_data.get('avg')
    _es_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    valoraciones_qs = ValoracionShowcooking.objects.filter(showcooking=showcookin).select_related('usuario').order_by('-fecha_creacion')
    if not _es_admin:
        valoraciones_qs = valoraciones_qs.filter(oculto=False)
    valoraciones = valoraciones_qs

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
        'url_avatar_chef': url_avatar_chef,
        'inicial_avatar_chef': inicial_avatar_chef,
        'url_perfil_chef': url_perfil_chef,
        'recetas': recetas,
        'avg_rating': avg_rating,
        'avg_rating_stars': _estrellas_valoracion_media(avg_rating),
        'num_valoraciones': rating_data.get('total') or 0,
        'embed_youtube_url': _youtube_embed_url(showcookin.url_youtube),
        'video_url_original': showcookin.url_youtube,
        'is_favorite': is_favorite,
        'valoracion_form': valoracion_form,
        'valoraciones': valoraciones,
        'valoracion_usuario_puntuacion': valoracion_usuario_puntuacion,
        'es_admin': _es_admin,
    })
