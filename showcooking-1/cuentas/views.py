from django.shortcuts import render
from .models import UserAccount  # Assuming you have a UserAccount model in models.py

def user_dashboard(request):
    users = UserAccount.objects.all()  # Fetch all user accounts from the database
    return render(request, 'cuentas/user_dashboard.html', {'users': users})  # Render the user dashboard template with user data

def login_view(request):
    return render(request, 'cuentas/iniciosesion.html')  # Render the login template

def register_view(request):
    return render(request, 'cuentas/registro.html')  # Render the registration template