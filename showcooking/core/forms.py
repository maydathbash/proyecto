from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-input-custom',
            'placeholder': 'usuario',
            'id': 'username'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-custom form-control',
            'placeholder': '********',
            'id': 'password'
        })
    )