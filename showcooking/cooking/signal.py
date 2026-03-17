from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Showcooking, Chef_ShowCooking

@receiver(post_save, sender=Showcooking)
def validar_y_vincular_chef(sender, instance, created, **kwargs):
    # Esta app no tiene campo `creador` en Showcooking.
    # La vinculacion chef-showcooking se gestiona en las vistas de creacion.
    if not created:
        return