from django.db import models
from cuentas.models import Usuario

# Create your models here.
class inicios_de_sesion(models.Model):
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.username


def registrar_inicio_sesion(usuario, ip):
    return inicios_de_sesion.objects.create(usuario=usuario, ip=ip)