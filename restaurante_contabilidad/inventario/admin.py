from django.contrib import admin
from .models import Producto, CompraFactura

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'cantidad', 'codigo', 'fecha_creacion')  # Asegúrate de que 'fecha_creacion' esté en el modelo
    ordering = ['fecha_creacion']  # Asegúrate de que 'fecha_creacion' esté en el modelo


admin.site.register(Producto, ProductoAdmin)
admin.site.register(CompraFactura)