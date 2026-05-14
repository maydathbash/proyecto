# ShowCooking

Plataforma web de cocina donde los chefs pueden publicar sus showcookings y recetas. Los usuarios pueden valorarlos, comentar, guardar recetas favoritas y seguir a sus chefs preferidos.

Desarrollado con Django 6 y desplegado en Fly.io.

---

## Qué puedes hacer en la plataforma

- **Como visitante**: navegar por los showcookings publicados, ver recetas y buscar por título o descripción.
- **Como usuario registrado**: valorar con estrellas, comentar, guardar recetas y marcar showcookings como favoritos.
- **Como chef**: crear y gestionar tus propios showcookings con vídeo de YouTube, añadir recetas con ingredientes por grupos y pasos de preparación detallados.
- **Como administrador**: ocultar contenido o valoraciones desde el propio sitio sin necesidad de entrar al panel de Django.

---

## Stack

- **Python 3.14** + **Django 6**
- **SQLite3** como base de datos
- **Whitenoise** para servir estáticos en producción
- **Pillow** para gestionar imágenes subidas
- **Fly.io** para el despliegue

---

## Requisitos

- Python 3.14+
- pip

---

## Instalación y arranque en local

```bash
# 1. Clonar el repositorio
git clone https://github.com/maydathbash/proyecto.git
cd proyecto/showcooking

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r ../requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Recopilar estáticos
python manage.py collectstatic --noinput

# 6. Crear un superusuario (opcional)
python manage.py createsuperuser

# 7. Arrancar
python manage.py runserver
```

Abre `http://localhost:8000` en el navegador.  
El panel de administración está en `http://localhost:8000/admin/`.

Si quieres que sea accesible desde otros dispositivos en la misma red:

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Variables de entorno

El proyecto lee su configuración de variables de entorno. Puedes definirlas en un archivo `.env` o exportarlas directamente.

| Variable | Por defecto | Descripción |
|---|---|---|
| `SECRET_KEY` | clave insegura incluida | Clave secreta de Django. Cámbiala en producción. |
| `DEBUG` | `False` | Activa el modo debug (`1`, `true`, `yes`...) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.fly.dev` | Hosts permitidos, separados por coma |
| `CSRF_TRUSTED_ORIGINS` | `https://*.fly.dev` | Orígenes de confianza para CSRF |
| `SERVE_MEDIA` | `True` | Sirve `/media/` desde Django en producción |

---

## Estructura del proyecto

```
proyecto/
├── requirements.txt
├── README.md
├── DOCUMENTACION.md       # documentación técnica detallada
└── showcooking/
    ├── manage.py
    ├── fly.toml
    ├── showcooking/       # configuración central
    ├── cooking/           # showcookings y recetas
    ├── cuentas/           # usuarios, chefs y autenticación
    ├── interacciones/     # valoraciones, favoritos y comentarios
    ├── core/              # páginas generales
    ├── static/            # CSS, JS e imágenes del sitio
    └── media/             # archivos subidos por usuarios
```

---

## Despliegue

El proyecto está configurado para Fly.io. Con la CLI de Fly instalada:

```bash
cd showcooking
fly deploy
```

Asegúrate de tener las variables de entorno configuradas en Fly antes de desplegar:

```bash
fly secrets set SECRET_KEY="tu_clave_secreta"
fly secrets set DEBUG=false
fly secrets set ALLOWED_HOSTS=showcooking.fly.dev
fly secrets set CSRF_TRUSTED_ORIGINS=https://showcooking.fly.dev
```

---

## Documentación

Para más detalles sobre modelos, vistas, URLs y configuración consulta [DOCUMENTACION.md](DOCUMENTACION.md).
