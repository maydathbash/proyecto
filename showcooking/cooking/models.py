from django.db import models
from django.conf import settings
from cuentas.models import Usuario,Chef 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from urllib.parse import parse_qs, urlparse
# Create your models here.

class Categoria_receta(models.Model):
    nombre = models.CharField(max_length=100)
    id=models.AutoField(primary_key=True)
    
    def __str__(self):
        return self.nombre
class categoria_showcooking(models.Model):
    id=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=20)
    
    def __str__(self):
        return self.nombre
    
class Showcooking(models.Model):
    Estado_Showcooking = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
    ]
    
    id=models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to='imagenes/', null=False, blank=False)
    titulo = models.CharField(max_length=20)
    descripcion = models.TextField()
    url_youtube = models.URLField( blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    publicado = models.CharField(max_length=10, choices=Estado_Showcooking, default='borrador')
    categoria = models.ForeignKey(categoria_showcooking, on_delete=models.CASCADE, null=False , blank=False)
    Dificultad_Niveles = [
        ('facil', 'Fácil'),
        ('intermedio', 'Intermedio'),
        ('dificil', 'Difícil'),
    ]
    dificultad = models.CharField(max_length=15, choices=Dificultad_Niveles, default='intermedio')

    
    def youtube_id(self):
        if not self.url_youtube:
            return None
        val = str(self.url_youtube).strip()
        if val.startswith('www.'):
            val = f'https://{val}'

        parsed = urlparse(val)
        host = (parsed.netloc or '').lower()
        path = parsed.path or ''

        if 'youtu.be' in host:
            return path.strip('/').split('/')[0] or None

        if 'youtube.com' in host or 'youtube-nocookie.com' in host:
            parts = [p for p in path.split('/') if p]
            if parts and parts[0] in ('shorts', 'live', 'v', 'embed') and len(parts) > 1:
                return parts[1]
            return parse_qs(parsed.query).get('v', [None])[0]

        return None
    def __str__(self):
        return self.titulo
class Receta(models.Model):
    showcooking = models.ForeignKey(
        Showcooking,
        on_delete=models.CASCADE,
        related_name='recetas'
    )
    Estado_Receta = [
        ('borrador', 'Borrador'),
        ('publicada', 'Publicada'),
    ]
    
    imagen=models.ImageField(upload_to='recetas/', null=False, blank=False, default='recetas/default.jpg')
    id=models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    instrucciones = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=Estado_Receta, default='borrador')
    
    categoria = models.ForeignKey(Categoria_receta, on_delete=models.SET_NULL, null=True)

#probar a ver como funciona el foreignkey
class Chef_ShowCooking(models.Model):
    id_showcooking=models.ForeignKey(Showcooking, on_delete=models.CASCADE)
    id_chef=models.ForeignKey('cuentas.Chef', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.id_chef} -> {self.id_showcooking}"
class Chef_Recetas(models.Model):
    id_chef=models.ForeignKey('cuentas.Chef', on_delete=models.CASCADE)
    id_receta=models.ForeignKey(Receta, on_delete=models.CASCADE)

class ingredientes(models.Model):
    id=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=40)
class ingredientes_receta(models.Model):
    id_Receta=models.ForeignKey(Receta, on_delete=models.CASCADE)
    id_ingrediente=models.ForeignKey(ingredientes, on_delete=models.SET_DEFAULT, default="AA")
    cantidad=models.BigIntegerField()    
    

