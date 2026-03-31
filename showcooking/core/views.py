from django.shortcuts import render, redirect
from django.db.models import Avg, Count, Q
from cooking.models import Receta, Showcooking
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.apps import apps
from django.urls import reverse, NoReverseMatch

# Create your views here.
def index(request):
    query = (request.GET.get('q', '') or '').strip()
    form = AuthenticationForm()

    base_busqueda_qs = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    )

    if query:
        show2 = base_busqueda_qs.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        ).order_by('-fecha_creacion')
    else:
        # Sin query mostramos ultimos publicados para que la seccion sea util.
        show2 = base_busqueda_qs.order_by('-fecha_creacion')[:8]

    mejores_showcookings = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[:3]

    mejores_showcookings2 = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[3:6]

    showcookings_famosos = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones', '-fecha_creacion')[:6]

    show = Showcooking.objects.order_by('-fecha_creacion')[:6]

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core-index')

    contexto = {
        'mejores_showcookings': mejores_showcookings,
        'mejores_showcookings2': mejores_showcookings2,
        'showcookings_famosos': showcookings_famosos,
        'show': show,
        'query': query,
        'busqueda': show2,
        'search_active': bool(query),
        'total_resultados': (show2.count() if hasattr(show2, 'count') else len(show2)),
        'form': form,
    }

    user = request.user
    es_admin_attr = getattr(user, 'es_admin', None)
    panel_es_admin = False
    if user.is_authenticated:
        if callable(es_admin_attr):
            try:
                panel_es_admin = bool(es_admin_attr())
            except Exception:
                panel_es_admin = False
        panel_es_admin = panel_es_admin or user.is_staff or user.is_superuser

    contexto['panel_is_admin'] = user.is_authenticated and (
        panel_es_admin
    )
    contexto['panel_is_chef'] = _is_chef_user(user)
    contexto['create_showcooking_url'] = _get_create_showcooking_url()

    if request.headers.get('HX-Request'):
        return render(request, 'partials/lista_cookings.html', contexto)

    return render(request, 'core/index.html', contexto)


def recetas(request):
    query = (request.GET.get('q', '') or '').strip()
    recetas_qs = Receta.objects.filter(
        Q(estado='publicada') | Q(estado='publicado')
    ).annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    )

    if query:
        recetas_qs = recetas_qs.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        )

    recetas_qs = recetas_qs.order_by('-avg_rating', '-num_valoraciones', '-fecha_creacion')

    return render(request, 'core/recetas.html', {
        'recetas': recetas_qs,
        'query': query,
        'total_recetas': recetas_qs.count(),
    })


def cerrar_sesion(request):
    logout(request)
    return redirect('core-index')


def _is_chef_user(user):
    if not user.is_authenticated:
        return False
    rol = getattr(getattr(user, 'tipo_usuario', None), 'nombre_rol', '') or ''
    return rol.strip().lower() in {'chef', 'cocinero'}


# Dashboard para chefs: muestra showcookings creados por el chef actual
from cooking.models import Chef_ShowCooking
from cuentas.models import Chef
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_chef(request):
    user = request.user
    # Buscar el objeto Chef asociado al usuario
    chef_obj = Chef.objects.filter(nombre=user.first_name, apellidos=user.last_name).first()
    showcookings = []
    if chef_obj:
        showcooking_links = Chef_ShowCooking.objects.filter(id_chef=chef_obj)
        showcookings = [link.id_showcooking for link in showcooking_links]

    contexto = {
        'showcookings': showcookings,
        'chef_obj': chef_obj,
    }
    return render(request, 'core/dashboard_chef.html', contexto)


def _get_create_showcooking_url():
    for name in ('crear_showcooking', 'showcooking-crear', 'crear_show'):
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return None