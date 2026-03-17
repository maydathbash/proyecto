from django import forms

from .models import Showcooking, Receta, categoria_showcooking, Categoria_receta
from cuentas.models import Chef


class ShowcookingForm(forms.ModelForm):
    chef = forms.ModelChoiceField(
        queryset=Chef.objects.all(),
        label='Chef asignado',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Selecciona un chef'
    )

    nueva_categoria = forms.CharField(
        required=False,
        label='Crear nueva categoria',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej.: Cocina internacional',
        })
    )

    class Meta:
        model = Showcooking
        fields = ['titulo', 'descripcion', 'imagen', 'url_youtube', 'categoria', 'dificultad', 'publicado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'url_youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'dificultad': forms.Select(attrs={'class': 'form-select'}),
            'publicado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields([
            'chef', 'titulo', 'descripcion', 'imagen', 'url_youtube',
            'categoria', 'nueva_categoria', 'dificultad', 'publicado'
        ])

    def save(self, commit=True):
        instance = super().save(commit=False)

        nueva = (self.cleaned_data.get('nueva_categoria') or '').strip()
        if nueva:
            categoria_obj, _ = categoria_showcooking.objects.get_or_create(nombre=nueva)
            instance.categoria = categoria_obj

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class RecetaShowcookingForm(forms.ModelForm):
    chef = forms.ModelChoiceField(
        queryset=Chef.objects.all(),
        label='Chef asignado',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Selecciona un chef'
    )

    nueva_categoria = forms.CharField(
        required=False,
        label='Crear nueva categoria',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej.: Postres, Pasta, Vegetariana...',
        })
    )

    class Meta:
        model = Receta
        fields = ['titulo', 'descripcion', 'instrucciones', 'imagen', 'categoria', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instrucciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields([
            'chef', 'titulo', 'descripcion', 'instrucciones', 'imagen',
            'categoria', 'nueva_categoria', 'estado'
        ])

    def save(self, commit=True):
        instance = super().save(commit=False)

        nueva = (self.cleaned_data.get('nueva_categoria') or '').strip()
        if nueva:
            categoria_obj, _ = Categoria_receta.objects.get_or_create(nombre=nueva)
            instance.categoria = categoria_obj

        if commit:
            instance.save()
            self.save_m2m()
        return instance
