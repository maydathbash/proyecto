from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Chef

@receiver(post_save, sender=Usuario)
def manejar_perfil_chef(sender, instance, created, **kwargs):
    # Solo actuamos si el usuario se acaba de crear
    if created and instance.tipo_usuario == 'cocinero':
        try:
            Chef.objects.get_or_create(usuario=instance)
        except Exception:
            # Esto evita que el createsuperuser explote si hay problemas de DB
            pass