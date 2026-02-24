from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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
    def es_admin(self):
        if self.tipo_usuario == 'Administrador':
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
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='perfil_chef'
    )
    