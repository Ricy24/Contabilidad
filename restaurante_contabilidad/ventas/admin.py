from django.contrib import admin
from .models import Venta, DetalleVenta, Factura, Cliente


# Configuración de Cliente
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'email', 'direccion')
    search_fields = ('nombre', 'email')
    list_filter = ('nombre',)


# Configuración de Venta
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('cliente',)
    search_fields = ('cliente__nombre', 'producto')


# Configuración de Detalle de Venta
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('venta__id', 'producto__nombre')


# Configuración de Factura
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_factura', 'cliente', 'fecha_emision', 'venta')
    search_fields = ('numero_factura', 'cliente__nombre')
    list_filter = ('fecha_emision',)

    def numero(self, obj):
        return f"Factura-{obj.id}"


# Registro en el administrador de Django
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(DetalleVenta, DetalleVentaAdmin)
admin.site.register(Factura, FacturaAdmin)
