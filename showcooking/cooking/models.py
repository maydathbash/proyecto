from django.db import models
from django.conf import settings
from cuentas.models import Usuario,Chef 
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from urllib.parse import parse_qs, urlparse
import re
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
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    url_youtube = models.URLField( blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    visitas = models.PositiveIntegerField(default=0)
    
    publicado = models.CharField(max_length=10, choices=Estado_Showcooking, default='borrador')
    oculto = models.BooleanField(default=False)
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

    @property
    def relacion_creador(self):
        prefetched = getattr(self, '_prefetched_objects_cache', {})
        relations = prefetched.get('chef_showcooking_set')
        if relations is not None:
            return relations[0] if relations else None
        return self.chef_showcooking_set.select_related('id_chef').first()

    @property
    def chef_creador(self):
        relacion = self.relacion_creador
        return relacion.id_chef if relacion else None

    @property
    def nombre_creador(self):
        chef = self.chef_creador
        return str(chef) if chef else 'Sin chef asignado'

    @property
    def url_avatar_creador(self):
        chef = self.chef_creador
        return chef.url_avatar_visible if chef else None

    @property
    def inicial_creador(self):
        chef = self.chef_creador
        return chef.inicial_visible if chef else 'S'

    @property
    def url_perfil_creador(self):
        chef = self.chef_creador
        return chef.url_perfil_publico if chef else None

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
    visitas = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=10, choices=Estado_Receta, default='borrador')
    oculto = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria_receta, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def url_avatar_autor(self):
        if getattr(self.autor, 'avatar', None):
            try:
                return self.autor.avatar.url
            except Exception:
                pass
        return None

    @property
    def inicial_autor(self):
        inicial = getattr(self.autor, 'avatar_initial', None)
        if inicial:
            return inicial
        base = (getattr(self.autor, 'username', '') or 'R').strip()
        return base[:1].upper() if base else 'R'

    @property
    def url_perfil_autor(self):
        return getattr(self.autor, 'url_perfil_publico', None)

    @property
    def pasos_instrucciones(self):
        pasos = []
        for indice, linea in enumerate((self.instrucciones or '').splitlines(), start=1):
            paso = linea.strip()
            if not paso:
                continue
            paso = re.sub(r'^(?:paso\s*)?\d+[\).:-]?\s*', '', paso, flags=re.IGNORECASE)
            paso = re.sub(r'^[-*•]\s*', '', paso)
            if paso:
                if '||' in paso:
                    titulo, descripcion = paso.split('||', 1)
                    titulo = titulo.strip() or f'Paso {indice}'
                    descripcion = descripcion.strip()
                else:
                    titulo = f'Paso {indice}'
                    descripcion = paso
                pasos.append({
                    'titulo': titulo,
                    'descripcion': descripcion,
                })
        return pasos

    @property
    def ingredientes_detallados(self):
        return [
            {
                'grupo': ingrediente.bloque_preparacion or 'Ingredientes principales',
                'cantidad': ingrediente.cantidad,
                'nombre': ingrediente.id_ingrediente.nombre,
            }
            for ingrediente in self.ingredientes_items.select_related('id_ingrediente').all()
            if ingrediente.id_ingrediente_id
        ]

    @property
    def ingredientes_agrupados(self):
        grupos = []
        indice_por_titulo = {}

        for ingrediente in self.ingredientes_detallados:
            titulo = ingrediente.get('grupo') or 'Ingredientes principales'
            if titulo not in indice_por_titulo:
                indice_por_titulo[titulo] = len(grupos)
                grupos.append({
                    'titulo': titulo,
                    'items': [],
                })
            grupos[indice_por_titulo[titulo]]['items'].append(ingrediente)

        return grupos

#probar a ver como funciona el foreignkey
class Chef_ShowCooking(models.Model):
    id_showcooking=models.ForeignKey(Showcooking, on_delete=models.CASCADE, null=False, blank=False)
    id_chef=models.ForeignKey('cuentas.Chef', on_delete=models.CASCADE, null=False, blank=False)
    def __str__(self):
        return f"{self.id_chef} -> {self.id_showcooking}"
class Chef_Recetas(models.Model):
    id_chef=models.ForeignKey('cuentas.Chef', on_delete=models.CASCADE, null=False, blank=False)
    id_receta=models.ForeignKey(Receta, on_delete=models.CASCADE, null=False, blank=False)

class ingredientes(models.Model):
    id=models.AutoField(primary_key=True)
    nombre=models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class ingredientes_receta(models.Model):
    id_Receta=models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='ingredientes_items')
    id_ingrediente=models.ForeignKey(ingredientes, on_delete=models.CASCADE, related_name='recetas_asociadas')
    bloque_preparacion=models.CharField(max_length=80, blank=True, default='')
    cantidad=models.CharField(max_length=60)

    class Meta:
        ordering = ['id']

    def __str__(self):
        bloque = f" ({self.bloque_preparacion})" if self.bloque_preparacion else ''
        return f"{self.cantidad} de {self.id_ingrediente}{bloque}"
    

