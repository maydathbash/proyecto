from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-input-custom email',
            'placeholder': 'usuario',
            'id': 'username',
            'aria-describedby': 'usuario-help',
            'aria-required' : 'true'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-custom form-control contraseña',
            'placeholder': '********',
            'id': 'password',
            'aria-required' : 'true',
            'aria-describedby' : 'password-help'
        })
    )