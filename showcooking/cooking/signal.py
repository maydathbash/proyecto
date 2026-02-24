from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
from .models import Showcooking, Chef_ShowCooking

@receiver(post_save, sender=Showcooking)
def validar_y_vincular_chef(sender, instance, created, **kwargs):
    if created:
        # 1. Intentamos obtener el perfil de chef del creador
        # Usamos hasattr para verificar si existe la relación OneToOne
        if hasattr(instance.creador, 'perfil_chef'):
            # Si es chef, lo añadimos a la relación ManyToMany
            Chef_ShowCooking.objects.create(
                id_showcooking=instance,
                id_chef=instance.creador  # Usamos el objeto Usuario
            )
        else:
            # 2. Si no es chef, borramos el showcooking recién creado
            # y lanzamos un error para detener el proceso.
            instance.delete()
            raise PermissionDenied(
                f"Error: El usuario {instance.creador.username} no es un Chef. "
                "No se puede crear un Showcooking sin un perfil de Chef asociado."
            )