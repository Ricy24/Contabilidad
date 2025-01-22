from django.db import models
from inventario.models import Producto
import uuid  # Para generar identificadores únicos


# Modelo de Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    es_temporal = models.BooleanField(default=False)

    def str(self):
        return self.nombre

# Modelo de Venta
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    producto = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    

    def str(self):
        return f"Venta {self.id} - Cliente: {self.cliente.nombre if self.cliente else 'Sin cliente'}"

# Modelo de Detalle de Venta
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} - {self.cantidad}"
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Factura(models.Model):
    # Relación con otros modelos
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    # Campos adicionales
    imagen = models.ImageField(upload_to='facturas/')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    numero_factura = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Agregado para evitar problemas
    
    # Campos nuevos que has solicitado
    cedula_cliente = models.CharField(max_length=20, null=True, blank=True)  # Campo para la cédula del cliente
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        # Agregar más tipos de pago si es necesario
    ]
    tipo_pago = models.CharField(
        max_length=10,
        choices=TIPO_PAGO_CHOICES,
        default='efectivo',
    )

    def __str__(self):
        return f"Factura {self.id} - {self.cliente.nombre}"