from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator



class ValoracionShowcooking(models.Model):
    """Valoraciones de showcookings (1-5 estrellas)"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_showcooking'
    )
    
    showcooking = models.ForeignKey(
        'cooking.Showcooking',
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 = Malo, 5 = Excelente"
    )
    
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'showcooking']  # 1 valoración por usuario
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario} - {self.showcooking}: {self.puntuacion}★"

class ValoracionReceta(models.Model):
    """Valoraciones de recetas (1-5 estrellas)"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_receta'
    )
    
    receta = models.ForeignKey(
        'cooking.Receta',
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    
    class Meta:
        unique_together = ['usuario', 'receta']  # 1 valoración por usuario
        
    
    def __str__(self):
        return f"{self.usuario} - {self.receta}: {self.puntuacion}★"

class Favorito_showcooking(models.Model):
    """Showcookings favoritos de usuarios"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    
    showcooking = models.ForeignKey(
        'cooking.Showcooking',
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'showcooking']  # No duplicados
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.usuario} ❤️ {self.showcooking}"
    
class RecetaGuardada(models.Model):
    """Recetas guardadas por usuarios"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recetas_guardadas'
    )
    
    receta = models.ForeignKey(
        'cooking.Receta',
        on_delete=models.CASCADE,
        related_name='guardada_por'
    )
    
    fecha_guardado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'receta']  # No duplicados
        ordering = ['-fecha_guardado']
    
    def __str__(self):
        return f"{self.usuario} saved {self.receta}"
    
class Comentarios_ShowCooking(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_showcooking'
    )
    
    showcooking = models.ForeignKey(
        'cooking.Showcooking',
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    comentario=models.CharField(max_length=150)
    fecha=models.DateTimeField(auto_now_add=True)
class Comentarios_Recetas(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_showcooking'
    )
    
    receta = models.ForeignKey(
        'cooking.Receta',
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    comentario=models.CharField(max_length=150)
    fecha=models.DateTimeField(auto_now_add=True)