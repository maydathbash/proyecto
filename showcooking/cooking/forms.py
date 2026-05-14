from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.db.models import Case, Count, IntegerField, Value, When

from .models import Showcooking, Receta, categoria_showcooking, Categoria_receta, ingredientes, ingredientes_receta
from cuentas.models import Chef


INGREDIENTES_COMUNES = [
    'sal',
    'aceite de oliva',
    'azucar',
    'harina',
    'huevos',
    'huevo',
    'leche',
    'mantequilla',
    'ajo',
    'cebolla',
    'tomate',
    'pimienta negra',
]


def _ingredientes_ordenados():
    prioridad = [
        When(nombre__iexact=nombre, then=Value(indice))
        for indice, nombre in enumerate(INGREDIENTES_COMUNES)
    ]
    return ingredientes.objects.annotate(
        num_usos=Count('recetas_asociadas'),
        prioridad_lista=Case(
            *prioridad,
            default=Value(len(INGREDIENTES_COMUNES)),
            output_field=IntegerField(),
        )
    ).order_by('prioridad_lista', '-num_usos', 'nombre')


class IngredienteChoiceField(forms.ModelChoiceField):
    CREATE_NEW_VALUE = '__new__'
    TYPED_NEW_PREFIX = '__typed__:'

    def to_python(self, value):
        if value == self.CREATE_NEW_VALUE:
            return None
        if isinstance(value, str) and value.startswith(self.TYPED_NEW_PREFIX):
            return value
        return super().to_python(value)

    def validate(self, value):
        if isinstance(value, str) and value.startswith(self.TYPED_NEW_PREFIX):
            return
        super().validate(value)


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
        }),
        max_length=categoria_showcooking._meta.get_field('nombre').max_length,
    )

    class Meta:
        model = Showcooking
        fields = ['titulo', 'descripcion', 'imagen', 'url_youtube', 'categoria', 'dificultad', 'publicado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'url_youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'dificultad': forms.Select(attrs={'class': 'form-select'}),
            'publicado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        chef_fijado = kwargs.pop('chef_fijado', None)
        super().__init__(*args, **kwargs)
        if chef_fijado is not None:
            self.fields['chef'].queryset = Chef.objects.filter(pk=chef_fijado.pk)
            self.fields['chef'].initial = chef_fijado
            self.fields['chef'].empty_label = None
            self.fields['chef'].disabled = True
            self.fields['chef'].help_text = 'Se usa automaticamente tu perfil de chef.'
        self.order_fields([
            'chef', 'titulo', 'descripcion', 'imagen', 'url_youtube',
            'categoria', 'nueva_categoria', 'dificultad', 'publicado'
        ])

    def clean(self):
        cleaned_data = super().clean()
        categoria_existente = cleaned_data.get('categoria')
        nueva_categoria = (cleaned_data.get('nueva_categoria') or '').strip()

        if nueva_categoria:
            cleaned_data['nueva_categoria'] = nueva_categoria
            categoria_obj = categoria_showcooking.objects.filter(nombre__iexact=nueva_categoria).first()
            if categoria_obj is None:
                categoria_obj = categoria_showcooking.objects.create(nombre=nueva_categoria)
            cleaned_data['categoria'] = categoria_obj
            self._errors.pop('categoria', None)
            return cleaned_data

        if categoria_existente is None:
            self.add_error('categoria', 'Selecciona una categoria o escribe una nueva.')

        return cleaned_data

    def save(self, commit=True):
        imagen_anterior = None
        if self.instance.pk:
            imagen_anterior = Showcooking.objects.filter(pk=self.instance.pk).values_list('imagen', flat=True).first()

        instance = super().save(commit=False)

        if commit:
            instance.save()
            self.save_m2m()
            nueva_imagen = getattr(instance.imagen, 'name', None)
            if imagen_anterior and imagen_anterior != nueva_imagen:
                almacenamiento = instance.imagen.storage
                if almacenamiento.exists(imagen_anterior):
                    almacenamiento.delete(imagen_anterior)
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
            'instrucciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Escribe la elaboracion como quieras: pasos, parrafos o explicaciones detalladas.',
            }),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        chef_inicial = kwargs.pop('chef_inicial', None)
        super().__init__(*args, **kwargs)
        if chef_inicial is not None and not self.is_bound:
            self.fields['chef'].initial = chef_inicial
            self.fields['chef'].help_text = 'Se selecciona tu perfil de chef por defecto, pero puedes cambiarlo.'
        self.fields['instrucciones'].label = 'Elaboracion'
        self.fields['instrucciones'].help_text = 'Anade cada paso con un titulo corto y lo que hay que hacer. Se guardaran como lista de elaboracion.'
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


class IngredienteRecetaForm(forms.ModelForm):
    id_ingrediente = IngredienteChoiceField(
        queryset=ingredientes.objects.none(),
        required=False,
        label='Ingrediente',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-ingrediente-select': 'true',
        }),
    )

    nuevo_ingrediente = forms.CharField(
        required=False,
        label='Crear ingrediente nuevo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej.: Pimienta negra',
        })
    )

    class Meta:
        model = ingredientes_receta
        fields = ['bloque_preparacion', 'id_ingrediente', 'cantidad']
        widgets = {
            'bloque_preparacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej.: Salsa, carne, salteado...',
            }),
            'id_ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej.: 200 g, 2 unidades, 1 cucharada',
            }),
        }
        labels = {
            'bloque_preparacion': 'Parte de la receta',
            'id_ingrediente': 'Ingrediente',
            'cantidad': 'Cantidad',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = _ingredientes_ordenados()
        self.fields['id_ingrediente'].queryset = queryset
        self.fields['id_ingrediente'].choices = [
            (IngredienteChoiceField.CREATE_NEW_VALUE, 'Crear ingrediente nuevo...'),
            *[(ingrediente.pk, ingrediente.nombre) for ingrediente in queryset],
        ]
        if 'DELETE' in self.fields:
            self.fields['DELETE'].widget = forms.HiddenInput()
            self.fields['DELETE'].required = False
        self.fields['bloque_preparacion'].required = False
        self.fields['id_ingrediente'].required = False
        self.fields['cantidad'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not self.has_changed():
            return cleaned_data

        ingrediente_obj = cleaned_data.get('id_ingrediente')
        nuevo_ingrediente = (cleaned_data.get('nuevo_ingrediente') or '').strip()
        if isinstance(ingrediente_obj, str) and ingrediente_obj.startswith(IngredienteChoiceField.TYPED_NEW_PREFIX):
            nuevo_ingrediente = ingrediente_obj[len(IngredienteChoiceField.TYPED_NEW_PREFIX):].strip()
            cleaned_data['nuevo_ingrediente'] = nuevo_ingrediente
            cleaned_data['id_ingrediente'] = None
            ingrediente_obj = None
        cantidad = (cleaned_data.get('cantidad') or '').strip()

        if ingrediente_obj and nuevo_ingrediente:
            raise forms.ValidationError('Elige un ingrediente existente o escribe uno nuevo, pero no las dos cosas.')

        if not ingrediente_obj and not nuevo_ingrediente:
            raise forms.ValidationError('Selecciona un ingrediente o escribe uno nuevo.')

        if not cantidad:
            self.add_error('cantidad', 'Indica la cantidad de este ingrediente.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        nuevo_ingrediente = (self.cleaned_data.get('nuevo_ingrediente') or '').strip()
        if nuevo_ingrediente:
            ingrediente_obj = ingredientes.objects.filter(nombre__iexact=nuevo_ingrediente).first()
            if ingrediente_obj is None:
                ingrediente_obj = ingredientes.objects.create(nombre=nuevo_ingrediente[:80])
            instance.id_ingrediente = ingrediente_obj

        if commit:
            instance.save()
        return instance


class BaseIngredienteRecetaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        tiene_ingredientes = False

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                continue

            ingrediente_obj = form.cleaned_data.get('id_ingrediente')
            nuevo_ingrediente = (form.cleaned_data.get('nuevo_ingrediente') or '').strip()
            cantidad = (form.cleaned_data.get('cantidad') or '').strip()
            if ingrediente_obj or nuevo_ingrediente or cantidad:
                tiene_ingredientes = True
                break

        if not tiene_ingredientes:
            raise forms.ValidationError('Anade al menos un ingrediente a la receta.')


IngredienteRecetaFormSet = inlineformset_factory(
    Receta,
    ingredientes_receta,
    form=IngredienteRecetaForm,
    formset=BaseIngredienteRecetaFormSet,
    fk_name='id_Receta',
    extra=0,
    can_delete=True,
)
