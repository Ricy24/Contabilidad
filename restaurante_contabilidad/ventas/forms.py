from django import forms
from .models import Venta, DetalleVenta, Cliente, Factura
from django.forms import DateTimeField
from datetime import datetime

# Formulario para la venta (simplificado, sin cliente)
class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['total', 'pagado']  # Solo total y pagado, eliminando cliente

# Inline formset para gestionar los detalles de la venta
DetalleVentaFormSet = forms.inlineformset_factory(
    Venta, DetalleVenta, fields=('producto', 'cantidad', 'precio_unitario'), extra=1
)

# Formulario para crear o actualizar un cliente (usado en la factura)
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email']  # Ajustado para solo incluir los campos necesarios

# Formulario para la factura
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['venta', 'cliente', 'imagen']  # No incluimos 'fecha_emision'

    # Agregamos el campo 'fecha_emision' como solo lectura y se asigna automáticamente
    fecha_emision = forms.DateTimeField(
        initial=datetime.now,  # Establece la fecha y hora actual
        disabled=True,  # Lo hace solo lectura
        widget=forms.TextInput(attrs={'readonly': 'readonly'})  # Para mostrar como solo lectura en la plantilla
    )
