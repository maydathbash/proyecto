from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from django.views.generic import CreateView, TemplateView

from .forms import *

# Create your views here.
def inicio_sesion(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core-index')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'cuentas/iniciosesion.html', {'form': form})

class RegistroUsuarioView(CreateView):
    template_name = 'cuentas/registro.html'
    form_class = CustomUserCreationForm
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response