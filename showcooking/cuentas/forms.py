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
        available_roles = Rol.objects.exclude(nombre_rol__iexact='Administrador').order_by('nombre_rol')
        self.fields['tipo_usuario'].queryset = available_roles
        self.fields['tipo_usuario'].empty_label = 'Selecciona tu perfil'

        field_config = {
            'username': {
                'label': 'Nombre de usuario',
                'help_text': 'Tu nombre de usuario unico',
                'attrs': {
                    'placeholder': 'Ejemplo: juan123',
                    'autocomplete': 'username',
                },
            },
            'email': {
                'label': 'Correo electronico',
                'help_text': 'Tu correo electronico para recibir las notificaciones',
                'attrs': {
                    'placeholder': 'tucorreo@ejemplo.com',
                    'autocomplete': 'email',
                },
            },
            'password1': {
                'label': 'Contrasena',
                'help_text': 'Minimo 8 caracteres. Combina letras y numeros para que sea mas segura.',
                'attrs': {
                    'placeholder': 'Crea una contrasena',
                    'autocomplete': 'new-password',
                },
            },
            'password2': {
                'label': 'Repite la contrasena',
                'help_text': 'Escribe la misma contrasena para confirmar.',
                'attrs': {
                    'placeholder': 'Repite la contrasena',
                    'autocomplete': 'new-password',
                },
            },
            'tipo_usuario': {
                'label': 'Perfil',
                'help_text': 'Elige el tipo de acceso con el que vas a participar',
                'attrs': {},
            },
        }

        for name, field in self.fields.items():
            config = field_config.get(name, {})
            if config.get('label'):
                field.label = config['label']
            if 'help_text' in config:
                field.help_text = config['help_text']
            field.widget.attrs.update(config.get('attrs', {}))
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

        if available_roles.count() == 1:
            self.fields['tipo_usuario'].initial = available_roles.first()
            self.fields['tipo_usuario'].required = False
            self.fields['tipo_usuario'].widget = forms.HiddenInput()

    def clean_tipo_usuario(self):
        tipo_usuario = self.cleaned_data.get('tipo_usuario')
        if tipo_usuario:
            return tipo_usuario

        available_roles = self.fields['tipo_usuario'].queryset
        if available_roles.count() == 1:
            return available_roles.first()

        raise forms.ValidationError('Selecciona un perfil valido.')

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
        fields = ["username", "first_name", "last_name", "email", "avatar", "biografia"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "biografia": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].label = 'Imagen de perfil'
        self.fields['avatar'].required = False
        self.fields['biografia'].label = 'Biografia'
        self.fields['biografia'].required = False


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = True
