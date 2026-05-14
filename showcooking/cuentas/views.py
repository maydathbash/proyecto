from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.apps import apps
from django.urls import reverse, NoReverseMatch
from django.contrib import messages
from django.db.models import Prefetch
from core.models import registrar_inicio_sesion
from .models import Chef

from .forms import *


AVATAR_COLOR_CLASS_MAP = {
    '#2d6a4f': 'avatar-bg-1',
    '#1d3557': 'avatar-bg-2',
    '#7f5539': 'avatar-bg-3',
    '#264653': 'avatar-bg-4',
    '#6d597a': 'avatar-bg-5',
    '#3a5a40': 'avatar-bg-6',
    '#6c757d': 'avatar-bg-7',
    '#0f4c5c': 'avatar-bg-8',
}

# Create your views here.
def _obtener_ip_cliente(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def inicio_sesion(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                registrar_inicio_sesion(user, _obtener_ip_cliente(request))
            except Exception:
                print("Error al registrar inicio de sesion")
            login(request, user)
            return redirect('core-index')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'cuentas/iniciosesion.html', {'form': form})


class RegistroUsuarioView(CreateView):
    template_name = 'cuentas/registro.html'
    form_class = CustomUserCreationForm
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        rol = getattr(form.cleaned_data.get('tipo_usuario'), 'nombre_rol', '') or ''
        if rol.strip().lower() in {'chef', 'cocinero'}:
            Chef.objects.get_or_create(nombre=username[:30], apellidos='')
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
        return response


def _get_chef_for_user(user):
    if not user or not user.is_authenticated:
        return None

    rol = getattr(getattr(user, 'tipo_usuario', None), 'nombre_rol', '') or ''
    if rol.strip().lower() not in {'chef', 'cocinero'}:
        return None

    nombre = (user.first_name or user.username or '').strip()
    apellidos = (user.last_name or '').strip()

    if not nombre:
        return None

    chef = Chef.objects.filter(
        nombre__iexact=nombre,
        apellidos__iexact=apellidos,
    ).first()

    if chef:
        return chef

    return Chef.objects.create(nombre=nombre[:30], apellidos=apellidos[:80])


def _is_admin_user(user):
    if not user.is_authenticated:
        return False

    es_admin_attr = getattr(user, 'es_admin', None)
    if callable(es_admin_attr):
        try:
            if es_admin_attr():
                return True
        except Exception:
            pass

    return bool(user.is_staff or user.is_superuser)


def _is_chef_user(user):
    if not user.is_authenticated:
        return False
    rol = getattr(getattr(user, 'tipo_usuario', None), 'nombre_rol', '') or ''
    return rol.strip().lower() in {'chef', 'cocinero'}


def _user_role(user):
    if _is_admin_user(user):
        return 'admin'
    if _is_chef_user(user):
        return 'chef'
    return 'registrado'


def _role_label(role):
    labels = {
        'admin': 'Administrador',
        'chef': 'Chef',
        'registrado': 'Usuario registrado',
    }
    return labels.get(role, 'Usuario')


def _get_image_url_from_obj(obj):
    if not obj:
        return None
    for name in ('foto_perfil', 'foto', 'imagen', 'avatar', 'profile_image'):
        val = getattr(obj, name, None)
        try:
            if val and hasattr(val, 'url'):
                return val.url
        except Exception:
            pass
    return None


def _user_filtered_queryset(model, user, chef_obj=None):
    if model is None:
        return None
    field_names = {f.name for f in model._meta.fields}

    candidates = []
    if 'usuario' in field_names:
        candidates.append({'usuario': user})
    if 'user' in field_names:
        candidates.append({'user': user})
    if 'autor' in field_names:
        candidates.append({'autor': user})
    if 'creador' in field_names:
        candidates.append({'creador': user})
    if 'chef' in field_names and chef_obj is not None:
        candidates.append({'chef': chef_obj})

    for flt in candidates:
        try:
            return model.objects.filter(**flt)
        except Exception:
            continue
    return model.objects.none()


def _order_recent(qs):
    if qs is None:
        return None
    field_names = {f.name for f in qs.model._meta.fields}
    for f in ('fecha_creacion', 'created_at', 'fecha', 'id'):
        if f in field_names:
            return qs.order_by(f'-{f}')
    return qs


def _extract_desc(obj):
    for f in ('descripcion', 'description', 'resumen', 'texto'):
        if hasattr(obj, f):
            return getattr(obj, f) or ''
    return ''


def _extract_title(obj):
    for f in ('titulo', 'title', 'nombre', 'name'):
        if hasattr(obj, f):
            return getattr(obj, f)
    return str(obj)


def _extract_image_url(obj):
    for f in ('imagen', 'foto', 'image'):
        val = getattr(obj, f, None)
        try:
            if val and hasattr(val, 'url'):
                return val.url
        except Exception:
            continue
    return None


def _avatar_data(user):
    initial = getattr(user, 'avatar_initial', None)
    color = getattr(user, 'avatar_bg_color', None)
    if not initial:
        base = (getattr(user, 'first_name', '') or getattr(user, 'username', '') or '?').strip()
        initial = base[:1].upper() if base else '?'
    if not color:
        color = '#414447'
    color_class = AVATAR_COLOR_CLASS_MAP.get(color, 'avatar-bg-7')
    return initial, color, color_class


def _get_user_showcookings(user, only_published=False):
    try:
        Showcooking = apps.get_model('cooking', 'Showcooking')
        ChefShowcooking = apps.get_model('cooking', 'Chef_ShowCooking')
    except LookupError:
        return None

    chef_obj = _get_chef_for_user(user)
    if not chef_obj:
        return Showcooking.objects.none()

    show_ids = ChefShowcooking.objects.filter(id_chef=chef_obj).values_list('id_showcooking_id', flat=True)
    prefetch_chef = Prefetch('chef_showcooking_set', queryset=ChefShowcooking.objects.select_related('id_chef'))
    qs = Showcooking.objects.filter(id__in=show_ids).prefetch_related(prefetch_chef).distinct()
    if only_published:
        qs = qs.filter(publicado='publicado')
    return _order_recent(qs)


def _get_user_recetas(user, only_published=False):
    try:
        Receta = apps.get_model('cooking', 'Receta')
    except LookupError:
        return None

    qs = Receta.objects.select_related('autor').filter(autor=user)
    if only_published:
        qs = qs.filter(estado='publicada')
    return _order_recent(qs)


def _find_saved_content(user):
    saved_showcookings = []
    saved_recetas = []

    try:
        Showcooking = apps.get_model('cooking', 'Showcooking')
    except LookupError:
        Showcooking = None

    try:
        Receta = apps.get_model('cooking', 'Receta')
    except LookupError:
        Receta = None

    try:
        inter_models = apps.get_app_config('interacciones').get_models()
    except LookupError:
        inter_models = []

    seen_show = set()
    seen_rec = set()

    for model in inter_models:
        fields = {f.name: f for f in model._meta.fields}
        user_field = next((n for n in ('usuario', 'user') if n in fields), None)
        if not user_field:
            continue

        show_field = None
        rec_field = None
        for f in model._meta.fields:
            rel = getattr(f, 'remote_field', None)
            rel_model = getattr(rel, 'model', None)
            if Showcooking and rel_model == Showcooking:
                show_field = f.name
            if Receta and rel_model == Receta:
                rec_field = f.name

        try:
            qs = model.objects.filter(**{user_field: user})
        except Exception:
            continue

        if show_field:
            for row in qs.select_related(show_field):
                obj = getattr(row, show_field, None)
                if obj and obj.id not in seen_show:
                    seen_show.add(obj.id)
                    saved_showcookings.append(obj)

        if rec_field:
            for row in qs.select_related(rec_field):
                obj = getattr(row, rec_field, None)
                if obj and obj.id not in seen_rec:
                    seen_rec.add(obj.id)
                    saved_recetas.append(obj)

    return saved_showcookings, saved_recetas


def _get_user_favorites_and_saved(user):
    favoritos_show = []
    recetas_guardadas = []

    try:
        FavoritoShowcooking = apps.get_model('interacciones', 'Favorito_showcooking')
        favoritos_show = [row.showcooking for row in FavoritoShowcooking.objects.select_related('showcooking').prefetch_related('showcooking__chef_showcooking_set__id_chef').filter(usuario=user)]
    except Exception:
        favoritos_show = []

    try:
        RecetaGuardada = apps.get_model('interacciones', 'RecetaGuardada')
        recetas_guardadas = [row.receta for row in RecetaGuardada.objects.select_related('receta__autor').filter(usuario=user)]
    except Exception:
        recetas_guardadas = []

    return favoritos_show, recetas_guardadas


def _get_create_showcooking_url():
    for name in ('crear_showcooking', 'showcooking-crear', 'crear_show'):
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return None


def _editable_chef_fields(chef):
    if not chef:
        return []
    skip = {'id', 'usuario', 'user', 'fecha_registro', 'fecha_creacion', 'created_at', 'avatar', 'nombre', 'apellidos'}
    out = []
    for f in chef._meta.fields:
        if f.name in skip:
            continue
        typ = f.get_internal_type()
        input_type = 'text'
        if typ in ('ImageField', 'FileField'):
            input_type = 'file'
        elif typ in ('EmailField',):
            input_type = 'email'
        elif typ in ('BooleanField',):
            input_type = 'checkbox'
        out.append({
            'name': f.name,
            'label': f.verbose_name.title(),
            'type': input_type,
            'value': getattr(chef, f.name, ''),
        })
    return out


def _save_chef_fields(request, chef):
    if not chef:
        return
    for item in _editable_chef_fields(chef):
        name = item['name']
        ftype = item['type']
        if ftype == 'file':
            if name in request.FILES:
                setattr(chef, name, request.FILES[name])
        elif ftype == 'checkbox':
            setattr(chef, name, request.POST.get(name) == 'on')
        else:
            if name in request.POST:
                setattr(chef, name, request.POST.get(name))
    chef.save()


def _sync_chef_identity_from_user(user, chef):
    if not chef or not user:
        return

    chef.nombre = (user.first_name or user.username or '').strip()[:30]
    chef.apellidos = (user.last_name or '').strip()[:80]
    chef.save(update_fields=['nombre', 'apellidos'])


class UsuarioDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'cuentas/usuario.html'
    login_url = ''

    def post(self, request, *args, **kwargs):
        if request.POST.get('profile_action') == 'avatar':
            avatar_form = UserAvatarForm(request.POST, request.FILES, instance=request.user)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, 'Foto de perfil actualizada correctamente.')
            else:
                messages.error(request, 'Selecciona una imagen valida para actualizar la foto de perfil.')
            return redirect('usuario-dashboard')

        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        chef = _get_chef_for_user(request.user)

        if user_form.is_valid():
            user = user_form.save()
            try:
                _sync_chef_identity_from_user(user, chef)
                _save_chef_fields(request, chef)
            except Exception:
                pass
            messages.success(request, 'Perfil actualizado correctamente.')
        else:
            messages.error(request, 'Revisa los campos del perfil.')

        return redirect('usuario-dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        chef = _get_chef_for_user(user)
        role = _user_role(user)

        own_show_qs = _get_user_showcookings(user)
        own_rec_qs = _get_user_recetas(user)
        fav_show, saved_rec = _get_user_favorites_and_saved(user)
        profile_initial, profile_avatar_bg, profile_avatar_class = _avatar_data(user)

        # Lo principal por rol
        if role == 'registrado':
            show_for_panel = fav_show
            rec_for_panel = saved_rec
        else:
            show_for_panel = list(own_show_qs[:8]) if own_show_qs is not None else []
            rec_for_panel = list(own_rec_qs[:8]) if own_rec_qs is not None else []

        context.update({
            'role': role,
            'role_label': _role_label(role),
            'is_admin': role == 'admin',
            'is_chef': role == 'chef',
            'profile_image_url': _get_image_url_from_obj(user) or _get_image_url_from_obj(chef),
            'profile_initial': profile_initial,
            'profile_avatar_bg': profile_avatar_bg,
            'profile_avatar_class': profile_avatar_class,
            'avatar_form': UserAvatarForm(instance=user),
            'user_form': UserProfileForm(instance=user),
            'chef_fields': _editable_chef_fields(chef),
            'showcookings': show_for_panel,
            'recetas': rec_for_panel,
            'saved_showcookings': fav_show[:8],
            'favorite_showcookings': fav_show[:8],
            'saved_recetas': saved_rec[:8],
            'stats': [
                {'label': 'Showcookings creados', 'value': (own_show_qs.count() if own_show_qs is not None else 0)},
                {'label': 'Recetas creadas', 'value': (own_rec_qs.count() if own_rec_qs is not None else 0)},
                {'label': 'Elementos guardados', 'value': len(fav_show) + len(saved_rec)},
            ],
            'create_showcooking_url': _get_create_showcooking_url(),
            'public_profile_url': reverse('usuario-publico', kwargs={'username': user.username}),
            'extract_desc': _extract_desc,
            'extract_title': _extract_title,
            'extract_image_url': _extract_image_url,
        })
        return context


class UsuarioPublicoView(TemplateView):
    template_name = 'cuentas/usuario_publico.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        username = self.kwargs.get('username')
        profile_user = get_object_or_404(User, username=username)
        chef = _get_chef_for_user(profile_user)

        role = _user_role(profile_user)
        profile_initial, profile_avatar_bg, profile_avatar_class = _avatar_data(profile_user)
        own_show_qs = _get_user_showcookings(profile_user, only_published=True)
        own_rec_qs = _get_user_recetas(profile_user, only_published=True)

        context.update({
            'profile_user': profile_user,
            'role': role,
            'role_label': _role_label(role),
            'profile_image_url': _get_image_url_from_obj(profile_user) or _get_image_url_from_obj(chef),
            'profile_initial': profile_initial,
            'profile_avatar_bg': profile_avatar_bg,
            'profile_avatar_class': profile_avatar_class,
            'showcookings': list(own_show_qs[:8]) if own_show_qs is not None else [],
            'recetas': list(own_rec_qs[:8]) if own_rec_qs is not None else [],
            'stats': [
                {'label': 'Showcookings publicados', 'value': (own_show_qs.count() if own_show_qs is not None else 0)},
                {'label': 'Recetas publicadas', 'value': (own_rec_qs.count() if own_rec_qs is not None else 0)},
            ],
            'extract_desc': _extract_desc,
            'extract_title': _extract_title,
            'extract_image_url': _extract_image_url,
        })
        return context