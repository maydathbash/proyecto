from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario
from cuentas.models import Chef

@receiver(post_save, sender=Usuario)
def manejar_perfil_chef(sender, instance, created, **kwargs):
    # Si el tipo de usuario es 'cocinero'
    if instance.tipo_usuario == 'cocinero':
        Chef.objects.get_or_create(usuario=instance)