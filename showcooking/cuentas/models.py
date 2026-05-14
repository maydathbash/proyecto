from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.urls import reverse, NoReverseMatch
import hashlib

class Rol(models.Model):
    id=models.AutoField(primary_key=True)
    nombre_rol= models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre_rol

class Usuario(AbstractUser):
    
    id=models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    tipo_usuario = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    biografia = models.TextField(default='Esta es mi biografía.', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"

    @property
    def avatar_initial(self):
        base = (self.first_name or self.username or "?").strip()
        return base[:1].upper() if base else "?"

    @property
    def avatar_bg_color(self):
        # Color estable por usuario para evitar que cambie en cada render.
        palette = [
            "#2d6a4f", "#1d3557", "#7f5539", "#264653",
            "#6d597a", "#3a5a40", "#6c757d", "#0f4c5c",
        ]
        key = self.username or self.email or str(self.pk or "")
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % len(palette)
        return palette[idx]

    @property
    def url_perfil_publico(self):
        try:
            return reverse('usuario-publico', kwargs={'username': self.username})
        except NoReverseMatch:
            return None

    def es_admin(self):
        if str(self.tipo_usuario) == "Administrador":
            return True
        else:
            return False
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

class Chef(models.Model):
    id=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=30)
    apellidos=models.CharField(max_length=80)
    avatar=models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        full = f"{self.nombre} {self.apellidos}".strip()
        return full or f"Chef {self.id}"

    @property
    def usuario_vinculado(self):
        first_name = (self.nombre or '').strip()
        last_name = (self.apellidos or '').strip()
        if not first_name:
            return None

        if last_name:
            usuario = Usuario.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
            ).first()
            if usuario:
                return usuario

        usuario = Usuario.objects.filter(username__iexact=first_name).first()
        if usuario:
            return usuario

        return Usuario.objects.filter(first_name__iexact=first_name).first()

    @property
    def url_avatar_visible(self):
        usuario = self.usuario_vinculado
        if usuario and getattr(usuario, 'avatar', None):
            try:
                return usuario.avatar.url
            except Exception:
                pass
        if getattr(self, 'avatar', None):
            try:
                return self.avatar.url
            except Exception:
                pass
        return None

    @property
    def inicial_visible(self):
        usuario = self.usuario_vinculado
        if usuario and getattr(usuario, 'avatar_initial', None):
            return usuario.avatar_initial
        base = (self.nombre or str(self) or 'S').strip()
        return base[:1].upper() if base else 'S'

    @property
    def url_perfil_publico(self):
        usuario = self.usuario_vinculado
        return usuario.url_perfil_publico if usuario else None
    