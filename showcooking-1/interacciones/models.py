from django.db import models

class Interaccion(models.Model):
    usuario = models.ForeignKey('cuentas.Usuario', on_delete=models.CASCADE)
    receta = models.ForeignKey('cooking.Receta', on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario de {self.usuario} sobre {self.receta}'

class Valoracion(models.Model):
    usuario = models.ForeignKey('cuentas.Usuario', on_delete=models.CASCADE)
    receta = models.ForeignKey('cooking.Receta', on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Valoración de {self.usuario} para {self.receta} - Puntuación: {self.puntuacion}'