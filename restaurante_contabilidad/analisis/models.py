# analisis/models.py
from django.db import models
from django.utils import timezone
from main.models import Empleado
from ventas.models import Venta
from inventario.models import CompraFactura
from decimal import Decimal, ROUND_HALF_UP

class ReporteFinanciero(models.Model):
    fecha = models.DateField()
    ingresos_ventas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    costos_compras = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    costos_nomina = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    utilidad_bruta = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    margen_utilidad = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-fecha']
        
    def calcular_utilidad(self):
        try:
            self.utilidad_bruta = (
                Decimal(str(self.ingresos_ventas)) - 
                (Decimal(str(self.costos_compras)) + Decimal(str(self.costos_nomina)))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            if self.ingresos_ventas and self.ingresos_ventas != 0:
                self.margen_utilidad = (
                    (self.utilidad_bruta / Decimal(str(self.ingresos_ventas))) * 100
                ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                self.margen_utilidad = Decimal('0.00')
        except:
            self.utilidad_bruta = Decimal('0.00')
            self.margen_utilidad = Decimal('0.00')
            
        return self.utilidad_bruta