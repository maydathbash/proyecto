from django.shortcuts import render
from django.db.models import Avg, Count, Q
from cooking.models import Receta, Showcooking
from django.contrib.auth import logout
from django.shortcuts import redirect


# Create your views here.
def index(request):
    # Obtener los 5 showcookings más recientes
    #ultimos_showcookings = Showcooking.objects.filter(publicado='publicado').order_by('-fecha_creacion')[:5]
    query = request.GET.get('q')
    
    # 2. Lógica de filtrado global
    if query:
        show2 = Showcooking.objects.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query) | Q(categoria__icontains=query),
            publicado='publicado' 
        ).order_by('-fecha_creacion')
    else:
        show2 = '';
        
    mejores_showcookings = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[:5]
    
    # Obtener las 5 recetas mejor valoradas
    mejores_recetas = Receta.objects.filter(estado='publicada').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[:5]
    
    show=Showcooking.objects.order_by('-fecha_creacion')[:5]
    
    contexto = {
        'mejores_showcookings': mejores_showcookings,
        'mejores_recetas': mejores_recetas,
        'show': show,
        'query': query, 
        'busqueda': show2,
    }
    
    return render(request, 'core/index.html', contexto)

def cerrar_sesion(request):
    logout(request)
    return redirect('core-index')