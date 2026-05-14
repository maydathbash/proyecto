# ShowCooking — Documentación del proyecto

## Índice

1. [¿De qué va el proyecto?](#1-de-qué-va-el-proyecto)
2. [Stack y dependencias](#2-stack-y-dependencias)
3. [Cómo está organizado el código](#3-cómo-está-organizado-el-código)
4. [Configuración](#4-configuración)
5. [Las apps de Django](#5-las-apps-de-django)
   - [cuentas](#51-cuentas)
   - [cooking](#52-cooking)
   - [interacciones](#53-interacciones)
   - [core](#54-core)
6. [Modelos y base de datos](#6-modelos-y-base-de-datos)
7. [URLs del proyecto](#7-urls-del-proyecto)
8. [Despliegue en Fly.io](#8-despliegue-en-flyio)
9. [Estáticos y archivos subidos](#9-estáticos-y-archivos-subidos)
10. [Cómo arrancarlo en local](#10-cómo-arrancarlo-en-local)

---

## 1. ¿De qué va el proyecto?

ShowCooking es una web de cocina hecha con Django 6. La idea principal es que los chefs puedan publicar sus *showcookings*, que básicamente son eventos culinarios con vídeo de YouTube y sus recetas asociadas. Cualquier usuario registrado puede valorar los contenidos con estrellas, comentar, guardar recetas para verlas más tarde o marcar showcookings como favoritos. También hay un panel de admin normal de Django y un dashboard propio para los chefs.

---

## 2. Stack y dependencias

El proyecto usa Python 3.14 con un entorno virtual incluido en `env/`. La base de datos es SQLite3, tanto en local como en producción (por ahora). Para despliegue se usa Fly.io.

Las dependencias van en `requirements.txt`:

| Paquete | Versión |
|---|---|
| Django | >=6.0, <6.1 |
| Pillow | >=11.0, <12.0 |
| Whitenoise | >=6.8, <7.0 |

Pillow es necesario para gestionar las imágenes de perfil, portadas y recetas. Whitenoise se encarga de servir los estáticos en producción sin necesidad de nginx.

---

## 3. Cómo está organizado el código

```
proyecto/
├── requirements.txt
├── DOCUMENTACION.md
└── showcooking/              # aquí vive todo el proyecto Django
    ├── manage.py
    ├── db.sqlite3
    ├── fly.toml
    ├── showcooking/          # configuración central (settings, urls, wsgi...)
    ├── cooking/              # showcookings y recetas
    ├── cuentas/              # usuarios, chefs y autenticación
    ├── interacciones/        # valoraciones, favoritos, guardados, comentarios
    ├── core/                 # página de inicio y vistas generales
    ├── static/               # CSS, JS e imágenes del propio sitio
    ├── staticfiles/          # salida de collectstatic
    └── media/                # lo que suben los usuarios
        ├── avatars/
        ├── imagenes/
        └── recetas/
```

Cada app tiene su propia carpeta de templates dentro de `templates/`.

---

## 4. Configuración

El archivo de configuración está en `showcooking/showcooking/settings.py`. Casi todo lo sensible se carga desde variables de entorno para poder cambiar el comportamiento sin tocar código.

### Variables de entorno disponibles

| Variable | Por defecto | Para qué sirve |
|---|---|---|
| `SECRET_KEY` | clave insegura incluida en el código | La clave secreta de Django. Hay que cambiarla sí o sí en producción. |
| `DEBUG` | `False` | Activa el modo depuración. Acepta `1`, `true`, `yes`, `on`... |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.fly.dev` | Hosts desde los que se acepta conexión, separados por coma. |
| `CSRF_TRUSTED_ORIGINS` | `https://*.fly.dev` | Orígenes de confianza para peticiones con CSRF. |
| `SERVE_MEDIA` | `True` | Si está activo, Django sirve `/media/` directamente cuando no hay DEBUG. |

### ALLOWED_HOSTS actual

```python
ALLOWED_HOSTS = ['*']   # acepta cualquier host o IP
```

> Ojo: esto está así para poder conectarse desde cualquier sitio durante el desarrollo. En producción conviene cambiarlo por el dominio real.

### Idioma y zona horaria

```python
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
```

### Usuario personalizado

El proyecto usa un modelo de usuario propio en lugar del de Django por defecto:

```python
AUTH_USER_MODEL = 'cuentas.Usuario'
```

---

## 5. Las apps de Django

### 5.1 `cuentas`

Se ocupa de todo lo relacionado con usuarios: registro, login, perfiles y roles. También hay un `Chef` como entidad separada del usuario, aunque ambos pueden estar vinculados por nombre y apellidos.

**Vistas:**

| Vista | URL | Qué hace |
|---|---|---|
| `inicio_sesion` | `/cuentas/login/` | Login con formulario personalizado. Guarda la IP en la base de datos. |
| `RegistroUsuarioView` | `/cuentas/registro/` | Registro de nuevos usuarios. Si el rol es Chef, también crea el objeto `Chef` automáticamente. |
| `UsuarioDashboardView` | `/cuentas/usuario/` | Panel privado del usuario. Solo accesible con sesión iniciada. |
| `UsuarioPublicoView` | `/cuentas/perfil/<username>/` | Perfil público de cualquier usuario. |

Hay signals en `signals.py` que se encargan de algunas acciones automáticas tras el registro.

---

### 5.2 `cooking`

El corazón del proyecto. Aquí están los showcookings, las recetas y los ingredientes.

**Vistas:**

| Vista | URL | Qué hace |
|---|---|---|
| `crear_showcooking` | `/cooking/crear/` | Solo para chefs. Crea un nuevo showcooking. |
| `editar_showcooking` | `/cooking/showcooking/<pk>/editar/` | Editar un showcooking ya creado. |
| `crear_receta_showcooking` | `/cooking/crear/<pk>/receta/` | Añadir una receta a un showcooking. |
| `editar_receta` | `/cooking/receta/<pk>/editar/` | Editar una receta existente. |
| `detalle_showcooking` | `/cooking/showcooking/<pk>/` | Página de detalle, con el vídeo de YouTube incrustado. |
| `detalle_receta` | `/cooking/receta/<pk>/` | Página de la receta con ingredientes por grupos y pasos de preparación. |

Los formularios principales son `ShowcookingForm`, `RecetaShowcookingForm` y `IngredienteRecetaFormSet`.

---

### 5.3 `interacciones`

Todo lo que los usuarios pueden hacer con el contenido: puntuar, comentar, guardar y marcar favoritos. También tiene vistas exclusivas para administradores para ocultar contenido que no debe verse.

**Vistas:**

| Vista | URL | Qué hace |
|---|---|---|
| `toggle_favorito_showcooking` | `.../favorito/showcooking/<pk>/toggle/` | Añade o quita de favoritos. |
| `toggle_receta_guardada` | `.../guardada/receta/<pk>/toggle/` | Guarda o elimina una receta de la lista personal. |
| `valorar_showcooking` | `.../valorar/showcooking/<pk>/` | Crea o actualiza la valoración (1 a 5 estrellas). |
| `valorar_receta` | `.../valorar/receta/<pk>/` | Igual pero para recetas. |
| `admin_ocultar_showcooking` | `.../admin/ocultar/showcooking/<pk>/` | Solo admins: oculta o muestra un showcooking. |
| `admin_ocultar_receta` | `.../admin/ocultar/receta/<pk>/` | Solo admins: oculta o muestra una receta. |
| `admin_ocultar_opinion_showcooking` | `.../admin/ocultar/opinion/showcooking/<pk>/` | Solo admins: oculta una valoración de showcooking. |
| `admin_ocultar_opinion_receta` | `.../admin/ocultar/opinion/receta/<pk>/` | Solo admins: oculta una valoración de receta. |

---

### 5.4 `core`

Las páginas más generales: el index, el listado de recetas, el cerrar sesión y el dashboard del chef.

**Vistas:**

| Vista | URL | Qué hace |
|---|---|---|
| `index` | `/` | Portada con los mejores showcookings, los últimos publicados y un buscador. |
| `recetas` | `/recetas/` | Listado general de recetas. |
| `cerrar_sesion` | `/cerrar_sesion/` | Cierra la sesión. |
| `dashboard_chef` | `/dashboard-chef/` | Panel del chef con sus showcookings y recetas. |

También tiene el modelo `inicios_de_sesion`, que guarda la IP y la fecha/hora de cada vez que alguien entra.

---

## 6. Modelos y base de datos

### App `cuentas`

**`Rol`** — solo tiene `id` y `nombre_rol`. Los valores usados son "Administrador", "Chef" y "Usuario" (o similar).

**`Usuario`** — extiende `AbstractUser` con estos campos extra:

| Campo | Tipo |
|---|---|
| `tipo_usuario` | FK → `Rol` |
| `fecha_registro` | DateTimeField (auto) |
| `avatar` | ImageField en `avatars/` |
| `biografia` | TextField |

Tiene propiedades calculadas: `avatar_initial` (primera letra del nombre), `avatar_bg_color` (color estable basado en hash del username), `url_perfil_publico` y `es_admin()`.

**`Chef`** — entidad separada con `nombre`, `apellidos` y `avatar`. Se vincula a `Usuario` de forma dinámica buscando por nombre y apellidos. Tiene propiedades para obtener el avatar visible (primero mira si el usuario vinculado tiene foto), la inicial y la URL del perfil.

---

### App `cooking`

**`Categoria_receta`** y **`categoria_showcooking`** — tablas sencillas con `id` y `nombre` para clasificar el contenido.

**`Showcooking`** — el modelo principal del proyecto:

| Campo | Descripción |
|---|---|
| `titulo` | Máximo 120 caracteres |
| `descripcion` | Texto libre |
| `imagen` | Portada del showcooking |
| `url_youtube` | Enlace al vídeo (opcional) |
| `visitas` | Contador incremental |
| `publicado` | `borrador` o `publicado` |
| `oculto` | Para moderación por admins |
| `categoria` | FK a `categoria_showcooking` |
| `dificultad` | `facil`, `intermedio` o `dificil` |

Tiene un método `youtube_id()` que extrae el ID del vídeo de distintos formatos de URL de YouTube (watch, shorts, live, youtu.be...). Las propiedades `chef_creador`, `nombre_creador`, `url_avatar_creador`, etc., tiran de la relación `Chef_ShowCooking`.

**`Receta`** — siempre pertenece a un `Showcooking`:

| Campo | Descripción |
|---|---|
| `instrucciones` | Una instrucción por línea. Si se usa `||` separa título del paso y descripción. |
| `estado` | `borrador` o `publicada` |
| `oculto` | Para moderación |
| `categoria` | FK a `Categoria_receta` (opcional) |

La propiedad `pasos_instrucciones` parsea el campo de instrucciones y devuelve una lista de pasos limpios. `ingredientes_agrupados` agrupa los ingredientes por bloque de preparación.

**`Chef_ShowCooking`** — tabla intermedia que relaciona `Chef` con `Showcooking` (muchos a muchos).

**`Ingrediente`** y **`Receta_Ingrediente`** — catálogo de ingredientes y su relación con cada receta, incluyendo cantidad y a qué bloque de preparación pertenecen.

---

### App `interacciones`

| Modelo | Qué guarda | Restricción |
|---|---|---|
| `ValoracionShowcooking` | Puntuación 1-5★ + comentario de un showcooking | Una por usuario y showcooking |
| `ValoracionReceta` | Puntuación 1-5★ + comentario de una receta | Una por usuario y receta |
| `Favorito_showcooking` | Showcooking marcado como favorito | Uno por usuario y showcooking |
| `RecetaGuardada` | Receta guardada para leer después | Una por usuario y receta |
| `Comentarios_ShowCooking` | Comentario corto (150 chars) en un showcooking | Sin límite |
| `Comentarios_Recetas` | Comentario corto (150 chars) en una receta | Sin límite |

Las valoraciones tienen campo `oculto` para que los admins puedan quitarlas de la vista sin borrarlas.

---

### App `core`

**`inicios_de_sesion`** — registra cada login con el usuario, la IP y la fecha/hora exacta.

---

## 7. URLs del proyecto

El archivo raíz `showcooking/urls.py` incluye las URLs de cada app con estos prefijos:

| Prefijo | App |
|---|---|
| `/` | `core` |
| `/cooking/` | `cooking` |
| `/cuentas/` | `cuentas` |
| `/interacciones/` | `interacciones` |
| `/admin/` | Django Admin |

El listado completo de rutas:

| URL | Nombre | Vista |
|---|---|---|
| `/` | `core-index` | Portada |
| `/recetas/` | `core-recetas` | Listado de recetas |
| `/cerrar_sesion/` | `cerrar_sesion` | Logout |
| `/dashboard-chef/` | `dashboard_chef` | Panel del chef |
| `/cuentas/login/` | `login` | Inicio de sesión |
| `/cuentas/registro/` | `registro_usuario` | Registro |
| `/cuentas/usuario/` | `usuario-dashboard` | Dashboard privado |
| `/cuentas/perfil/<username>/` | `usuario-publico` | Perfil público |
| `/cooking/crear/` | `crear_showcooking` | Crear showcooking |
| `/cooking/showcooking/<pk>/editar/` | `editar_showcooking` | Editar showcooking |
| `/cooking/crear/<pk>/receta/` | `crear_receta_showcooking` | Añadir receta |
| `/cooking/receta/<pk>/editar/` | `editar_receta` | Editar receta |
| `/cooking/receta/<pk>/` | `detalle_receta` | Ver receta |
| `/cooking/showcooking/<pk>/` | `detalle_showcooking` | Ver showcooking |
| `/interacciones/favorito/showcooking/<pk>/toggle/` | `toggle-favorito-showcooking` | Toggle favorito |
| `/interacciones/guardada/receta/<pk>/toggle/` | `toggle-receta-guardada` | Toggle receta guardada |
| `/interacciones/valorar/showcooking/<pk>/` | `valorar-showcooking` | Valorar showcooking |
| `/interacciones/valorar/receta/<pk>/` | `valorar-receta` | Valorar receta |
| `/interacciones/admin/ocultar/showcooking/<pk>/` | `admin-ocultar-showcooking` | Ocultar showcooking (admin) |
| `/interacciones/admin/ocultar/receta/<pk>/` | `admin-ocultar-receta` | Ocultar receta (admin) |
| `/interacciones/admin/ocultar/opinion/showcooking/<pk>/` | `admin-ocultar-opinion-showcooking` | Ocultar opinión (admin) |
| `/interacciones/admin/ocultar/opinion/receta/<pk>/` | `admin-ocultar-opinion-receta` | Ocultar opinión receta (admin) |

---

## 8. Despliegue en Fly.io

El proyecto está configurado para Fly.io desde el archivo `showcooking/fly.toml`:

```toml
app = 'showcooking'
primary_region = 'jnb'

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  memory = '1gb'
  cpus = 1
```

Algunos detalles a tener en cuenta:
- Django escucha en el puerto `8080` internamente; Fly.io se encarga de exponer el 443.
- El HTTPS está forzado. El proxy inyecta `X-Forwarded-Proto` y Django lo lee gracias a `SECURE_PROXY_SSL_HEADER`.
- Las máquinas se apagan solas cuando no hay tráfico, lo que ahorra recursos.

### Variables de entorno que hay que configurar en Fly.io

```
SECRET_KEY=<una clave larga y aleatoria>
DEBUG=false
ALLOWED_HOSTS=showcooking.fly.dev
CSRF_TRUSTED_ORIGINS=https://showcooking.fly.dev
SERVE_MEDIA=true
```

---

## 9. Estáticos y archivos subidos

### Archivos estáticos (CSS, JS, imágenes del sitio)

Los estáticos del proyecto están en `showcooking/static/`. Al hacer `collectstatic` se copian a `showcooking/staticfiles/`, que es lo que sirve Whitenoise en producción con compresión y nombres hasheados para cacheo.

### Archivos subidos por usuarios

Se guardan en `showcooking/media/`, organizado en tres carpetas:
- `avatars/` — fotos de perfil de usuarios y chefs
- `imagenes/` — portadas de showcookings
- `recetas/` — imágenes de recetas

En producción Django los sirve directamente cuando `SERVE_MEDIA=True`. No es lo ideal para mucho tráfico, pero funciona para el volumen actual.

---

## 10. Cómo arrancarlo en local

Primero asegúrate de estar dentro de la carpeta `showcooking/` y con el entorno virtual activado.

```bash
# Instalar dependencias (solo la primera vez)
pip install -r ../requirements.txt

# Aplicar migraciones
python manage.py migrate

# Recopilar estáticos
python manage.py collectstatic --noinput

# Crear un superusuario si no tienes ninguno
python manage.py createsuperuser

# Arrancar el servidor
python manage.py runserver              # solo accesible desde localhost
python manage.py runserver 0.0.0.0:8000 # accesible desde la red local
```

El sitio queda disponible en `http://localhost:8000`. El panel de administración en `/admin/`.

---

*Última actualización: mayo 2026*
