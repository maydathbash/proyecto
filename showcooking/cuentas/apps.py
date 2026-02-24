from django.apps import AppConfig


#resulta que el cocinero no hace falta que sea un usuario
#solo que sea guardar unos datos del que creo el showcooking o receta no mas
#asi que quitare el signal
class CuentasConfig(AppConfig):
    name = 'cuentas'
    #def ready(self):
        #import cuentas.signals
