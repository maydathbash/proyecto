from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Usuario


TIPO_USUARIO_CHOICES = [
        ('Registrado', 'Registrado'),
        ('cocinero', 'Cocinero'),
    ]

# Formulario de inicio de sesión
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
# Formulario de registro de usuario
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    tipo_usuario = forms.ChoiceField(
        label='Tipo de usuario',
        choices=TIPO_USUARIO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    biografia = forms.CharField(
        label='Biografía',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Cuénta algo sobre ti...', 'rows': 3}),
        required=False
    )
    avatar = forms.ImageField(
        label='Avatar',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('email', 'tipo_usuario')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto asegura que los campos por defecto (username, password) tengan clase Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = self.cleaned_data['tipo_usuario']
        
        if commit:
            user.save()
            # La señal 'post_save' se dispara justo aquí (cuando se hace user.save())
            if user.tipo_usuario == 'cocinero':
                # Accedemos al perfil creado por la señal y añadimos los datos extra del form
                perfil_chef = user.perfil_chef 
                perfil_chef.biografia = self.cleaned_data.get('biografia')
                perfil_chef.foto_chef = self.cleaned_data.get('avatar')
                perfil_chef.save()
        return user
    

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'tipo_usuario', 'password1', 'password2', 'biografia', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicamos estilos Bootstrap a todos los campos
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
