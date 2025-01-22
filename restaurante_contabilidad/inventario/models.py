from django.db import models
from django.db.models import Sum
import os
from datetime import datetime



class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)
    codigo = models.CharField(max_length=50, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class CompraFactura(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='facturas/compras/%Y/%m/%d/')
    telegram_message_id = models.CharField(max_length=100, blank=True, null=True)
    chat_id = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.imagen:
            fecha = datetime.now()
            path = f'facturas/compras/{fecha.year}/{fecha.month}/{fecha.day}'
            os.makedirs(f'media/{path}', exist_ok=True)
        super().save(*args, **kwargs)

    @classmethod
    def get_estadisticas(cls):
        return {
            'total_compras': cls.objects.count(),
            'monto_total': cls.objects.aggregate(Sum('total'))['total__sum'] or 0,
            'promedio_compra': cls.objects.aggregate(avg=models.Avg('total'))['avg'] or 0
        }