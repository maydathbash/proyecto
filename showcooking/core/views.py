from django.shortcuts import render, redirect
from django.db.models import Avg, Count, Q
from cooking.models import Receta, Showcooking
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def index(request):
    # Obtener los 5 showcookings más recientes
    #ultimos_showcookings = Showcooking.objects.filter(publicado='publicado').order_by('-fecha_creacion')[:5]
    query = request.GET.get('q', '')
    form = AuthenticationForm()
    
    # 2. Lógica de filtrado global
    if query:
        show2 = Showcooking.objects.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query) ,
            publicado='publicado' 
        ).order_by('-fecha_creacion')
    else:
        show2 = Showcooking.objects.none()
    
    
    mejores_showcookings = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[:3]

    mejores_showcookings2 = Showcooking.objects.filter(publicado='publicado').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[3:6]
    
    # Obtener las 5 recetas mejor valoradas
    mejores_recetas = Receta.objects.filter(estado='publicada').annotate(
        avg_rating=Avg('valoraciones__puntuacion'),
        num_valoraciones=Count('valoraciones')
    ).order_by('-avg_rating', '-num_valoraciones')[:3]

    
    show=Showcooking.objects.order_by('-fecha_creacion')[:6]
    
    if request.headers.get('HX-Request'):
        return render(request, 'partials/lista_cookings.html', contexto)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    contexto = {
        'mejores_showcookings': mejores_showcookings,
        'mejores_showcookings2' : mejores_showcookings2,
        'mejores_recetas': mejores_recetas,
        'show': show,
        'query': query, 
        'busqueda': show2,
        'form': form,
    }    
    
    return render(request, 'core/index.html', contexto)

def cerrar_sesion(request):
    logout(request)
    return redirect('core-index')