from django.contrib import admin
from .models import Empleado

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cargo', 'salario_por_hora', 'activo', 'fecha_ingreso')
    search_fields = ('nombre', 'cargo')
    list_filter = ('activo',)

admin.site.register(Empleado, EmpleadoAdmin)
