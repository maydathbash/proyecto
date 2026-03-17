from django import forms

from .models import (
    ValoracionReceta,
    ValoracionShowcooking,
)


class ValoracionShowcookingForm(forms.ModelForm):
    class Meta:
        model = ValoracionShowcooking
        fields = ["puntuacion", "comentario"]
        widgets = {
            "puntuacion": forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={"class": "form-select"},
            ),
            "comentario": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Opcional: cuentanos tu opinion", "class": "form-control"}
            ),
        }


class ValoracionRecetaForm(forms.ModelForm):
    class Meta:
        model = ValoracionReceta
        fields = ["puntuacion", "comentario"]
        widgets = {
            "puntuacion": forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={"class": "form-select"},
            ),
            "comentario": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Comparte tu opinion", "class": "form-control"}
            ),
        }
