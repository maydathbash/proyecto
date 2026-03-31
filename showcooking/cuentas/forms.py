from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.apps import apps
from cuentas.models import Rol

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Usuario"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"})
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    tipo_usuario = forms.ModelChoiceField(
        queryset=Rol.objects.none(),  # Se asigna correctamente en __init__
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Tipo de usuario"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "tipo_usuario")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Siempre excluye el rol Administrador, incluso tras errores de validación
        self.fields['tipo_usuario'].queryset = Rol.objects.exclude(nombre_rol__iexact='Administrador')
        for name, field in self.fields.items():
            if name != "tipo_usuario" and "class" not in field.widget.attrs:
                field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.tipo_usuario = self.cleaned_data.get("tipo_usuario")
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
