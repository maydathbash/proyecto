from django.db import models
from django.conf import settings
from cuentas.models import Usuario,Chef 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
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
        if "youtu.be" in self.url_youtube:
            return self.url_youtube.split("/")[-1]
        return self.url_youtube.split("v=")[-1].split("&")[0]
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
    id_chef=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default="Vacio")
    def __str__(self):
        # Retorna el username del autor
        return self.id_chef.username
class Chef_Recetas(models.Model):
    id_chef=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default="AA")
    id_receta=models.ForeignKey(Receta, on_delete=models.CASCADE)

class ingredientes(models.Model):
    id=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=40)
class ingredientes_receta(models.Model):
    id_Receta=models.ForeignKey(Receta, on_delete=models.CASCADE)
    id_ingrediente=models.ForeignKey(ingredientes, on_delete=models.SET_DEFAULT, default="AA")
    cantidad=models.BigIntegerField()    
    

