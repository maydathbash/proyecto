from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Chef

@receiver(post_save, sender=Usuario)
def manejar_perfil_chef(sender, instance, created, **kwargs):
    # La entidad Chef ahora se gestiona por separado y no se crea automaticamente desde Usuario.
    return