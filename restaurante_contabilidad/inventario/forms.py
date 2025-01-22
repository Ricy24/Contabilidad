from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'costo', 'cantidad', 'codigo']
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'costo': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if Producto.objects.filter(codigo=codigo).exists() and not self.instance.pk:
            raise forms.ValidationError("Ya existe un producto con este código.")
        return codigo

