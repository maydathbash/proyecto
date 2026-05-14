# Manual de usuario — ShowCooking

Bienvenido. Este manual es para que cualquier persona pueda usar la plataforma sin perderse, seas cocinero de domingo o chef profesional. No hace falta saber nada de informática, solo ganas de cocinar (o de ver cómo lo hacen otros).

---

## Lo primero: entrar a la web

Abre el navegador y escribe la dirección del servidor. Si estás en local será algo como `http://192.168.x.x:8000`. Si ya está desplegada en internet, usa la URL que te hayan dado.

Nada más entrar verás la portada con los showcookings más valorados y los últimos publicados. Puedes curiosear sin registrarte, pero para lo interesante (valorar, guardar recetas, comentar...) necesitas una cuenta.

---

## Crear una cuenta

1. Haz clic en **Registro** en la parte superior de la página.
2. Rellena el formulario:
   - **Nombre de usuario**: el que aparecerá en tu perfil. Ponle algo que te identifique.
   - **Email**: uno que uses de verdad, por si acaso.
   - **Contraseña**: que tenga al menos 8 caracteres y no sea "12345678", por favor.
   - **Rol**: aquí está la clave. Si eres un usuario normal deja "Usuario". Si vas a publicar showcookings y recetas, elige **Chef**.
3. Dale a **Registrarse** y listo, ya tienes cuenta y sesión iniciada.

> Si te has equivocado de rol o quieres cambiar algo de tu perfil, puedes editarlo desde tu panel de usuario.

---

## Iniciar sesión

Si ya tienes cuenta, haz clic en **Iniciar sesión**, escribe tu nombre de usuario y contraseña y ya está. La plataforma te recordará mientras no cierres sesión.

Para cerrar sesión busca la opción en el menú superior o ve a `/cerrar_sesion/`.

---

## Explorar la plataforma

### La portada

La portada está dividida en secciones:
- **Los más valorados**: los showcookings con mejor puntuación media. Si algo aparece aquí, merece la pena verlo.
- **Últimos publicados**: lo más reciente. Ideal para estar al día.
- **Buscador**: si buscas algo concreto, escribe el nombre del plato o del showcooking y filtra los resultados al momento.

### Ver un showcooking

Al hacer clic en cualquier showcooking verás:
- La portada y descripción del evento.
- El vídeo de YouTube incrustado (si el chef lo ha añadido).
- Las recetas que forman parte de ese showcooking.
- Las valoraciones y comentarios de otros usuarios.
- La dificultad: fácil, intermedio o difícil.

### Ver una receta

Desde el detalle del showcooking puedes entrar a cada receta. Ahí encontrarás:
- Los ingredientes organizados por grupos (por ejemplo, "Para la salsa", "Para la masa"...).
- Los pasos de preparación numerados y claros.
- La valoración media y los comentarios.

---

## Lo que puedes hacer como usuario registrado

### Valorar un showcooking o una receta

Debajo del contenido verás las estrellas de valoración. Haz clic en las que quieras (del 1 al 5) y confirma. Solo puedes dejar una valoración por contenido, pero puedes cambiarla cuando quieras.

### Comentar

Junto a las valoraciones hay un campo para dejar un comentario. Cuéntale al chef qué te pareció, si te salió bien la receta, o lo que quieras. Sé majo.

### Guardar recetas

¿Ves una receta que quieres hacer el fin de semana? Dale al botón de **Guardar**. La encontrarás en tu panel de usuario para no tener que buscarla de nuevo.

### Marcar showcookings como favoritos

Si hay un showcooking que te encanta, márcalo con el corazón. Desde tu perfil podrás acceder rápido a todos tus favoritos.

### Tu perfil

Ve a **Mi perfil** (o al icono de tu usuario en el menú). Desde ahí puedes:
- Editar tu foto de perfil y tu biografía.
- Ver tus recetas guardadas y tus favoritos.
- Revisar tu actividad en la plataforma.

---

## Si eres chef

Los chefs tienen acceso a funciones extra para publicar su propio contenido.

### El dashboard de chef

Ve a `/dashboard-chef/` o búscalo en el menú. Desde ahí tienes un resumen de todos tus showcookings y recetas: cuántos están publicados, cuántos en borrador y cuántas visitas llevan.

### Crear un showcooking

1. En el dashboard o en el menú, haz clic en **Crear showcooking**.
2. Rellena los datos:
   - **Título**: algo descriptivo y atractivo.
   - **Descripción**: cuenta de qué va el evento, qué vas a cocinar, para quién es...
   - **Imagen de portada**: sube una foto que entre por los ojos.
   - **URL de YouTube**: si tienes el vídeo grabado, pega aquí el enlace. Admite cualquier formato de YouTube (watch, shorts, youtu.be...).
   - **Categoría y dificultad**: ayuda a los usuarios a filtrar y saber qué se van a encontrar.
3. Guárdalo como **borrador** si todavía no está listo, o publícalo directamente.

> Un showcooking en borrador no lo ve nadie más que tú.

### Añadir recetas al showcooking

Un showcooking sin recetas está un poco vacío. Una vez creado, entra en él y haz clic en **Añadir receta**. Para cada receta puedes poner:

- **Título e imagen**: lo básico.
- **Descripción**: un par de líneas para enganchar.
- **Ingredientes**: añádelos uno a uno con su cantidad. Puedes agruparlos por bloques si la receta es compleja (por ejemplo, un grupo para la base y otro para la cobertura).
- **Instrucciones**: escribe un paso por línea. Si quieres que el paso tenga título propio, usa el separador `||` así:
  ```
  Preparar la masa || Mezcla la harina con el agua poco a poco hasta que quede homogéneo.
  Reposo || Deja reposar la masa tapada durante 30 minutos en un lugar cálido.
  ```
  Si no usas `||`, el sistema numera los pasos automáticamente.

### Editar o actualizar contenido

Para editar un showcooking o una receta entra en él y busca el botón de **Editar**. Solo aparece si eres el autor. Puedes cambiar cualquier campo, incluyendo el estado (borrador/publicado).

---

## Si eres administrador

Además de todo lo anterior, los administradores pueden moderar el contenido directamente desde la web sin entrar al panel de Django.

### Ocultar publicaciones

Si hay un showcooking o una receta que no debería estar visible (contenido inapropiado, error, lo que sea), puedes ocultarlo con el botón correspondiente. El contenido no se borra, simplemente deja de verse para los usuarios normales. Tú y el resto de admins sí lo veis.

### Ocultar valoraciones y comentarios

Si alguien deja una valoración o comentario que no procede, puedes ocultarlo de la misma forma. El autor no recibe notificación, simplemente deja de mostrarse.

### Panel de Django

Para tareas más avanzadas (crear categorías, gestionar roles, ver registros de acceso...) accede al panel en `/admin/` con tu usuario administrador.

---

## Preguntas frecuentes

**¿Puedo cambiar mi rol después de registrarme?**  
Sí, pero necesitas que un administrador te cambie el rol desde el panel de Django.

**¿Por qué no me aparece el botón de crear showcooking?**  
Porque tu rol no es Chef. Si te has registrado como usuario normal y quieres crear contenido, contacta con el administrador.

**He subido una foto y no se ve bien, ¿qué hago?**  
Asegúrate de que la imagen esté en formato JPG o PNG y que no pese demasiado. Para portadas de showcookings funcionan bien las imágenes horizontales de al menos 800px de ancho.

**¿Puedo valorar mi propio contenido?**  
Técnicamente sí, pero no tiene mucho sentido. El sistema permite una valoración por usuario, así que estarías "gastando" tu voto en ti mismo.

**El vídeo de YouTube no se carga, ¿por qué?**  
Revisa que la URL sea correcta y que el vídeo esté en público. Los vídeos privados o no listados no se pueden incrustar.

---

*Manual actualizado — mayo 2026*
