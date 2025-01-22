from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

# Modelo para el perfil, ahora independiente del User
class Perfil(models.Model):
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Perfil {self.id}"

class Configuracion(models.Model):
    nombre_restaurante = models.CharField(max_length=100)
    nit = models.CharField(max_length=20)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.nombre_restaurante

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)  # Campo para el nombre del empleado
    cargo = models.CharField(max_length=100)  # Cargo del empleado
    salario_por_hora = models.DecimalField(max_digits=10, decimal_places=2)  # Salario por hora
    activo = models.BooleanField(default=True)  # Si el empleado está activo
    fecha_ingreso = models.DateTimeField(auto_now_add=True)  # Fecha en la que el empleado fue ingresado

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return self.nombre

    def iniciar_turno(self):
        """Método para iniciar el turno del empleado, registra la hora de inicio"""
        turno = RegistroHoras.objects.create(
            empleado=self,
            fecha=timezone.now().date(),
            hora_inicio=timezone.now(),
        )
        return turno

    def finalizar_turno(self, turno_id):
        """Método para finalizar el turno del empleado, registra la hora de fin y calcula el pago"""
        try:
            turno = RegistroHoras.objects.get(id=turno_id)

            if turno.hora_fin:
                return turno  # El turno ya ha sido finalizado

            turno.hora_fin = timezone.now()

            # Calcular las horas trabajadas utilizando timedelta
            tiempo_trabajado = turno.hora_fin - turno.hora_inicio
            turno.horas_trabajadas = Decimal(tiempo_trabajado.total_seconds() / 3600)  # Convertir segundos a horas

            # Calcular el pago (ahora por horas trabajadas)
            turno.pago_calculado = turno.horas_trabajadas * self.salario_por_hora
            turno.save()
            return turno
        except RegistroHoras.DoesNotExist:
            return None  # El turno no existe

# Modelo para registrar las horas trabajadas de los empleados
class RegistroHoras(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)  # Relación con empleado
    fecha = models.DateField()  # Fecha del turno
    hora_inicio = models.DateTimeField()  # Hora de inicio del turno
    hora_fin = models.DateTimeField(null=True, blank=True)  # Hora de fin del turno
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Horas trabajadas
    pago_calculado = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Pago calculado

    class Meta:
        verbose_name = 'Registro de Horas'
        verbose_name_plural = 'Registros de Horas'

    def __str__(self):
        return f"Turno de {self.empleado.nombre} en {self.fecha}"

class ImpuestosMensuales(models.Model):
    fecha = models.DateField()
    ventas_totales = models.DecimalField(max_digits=12, decimal_places=2)
    iva_generado = models.DecimalField(max_digits=12, decimal_places=2)  # 19% en Colombia
    retencion_fuente = models.DecimalField(max_digits=12, decimal_places=2)
    ica = models.DecimalField(max_digits=12, decimal_places=2)
    pagado = models.BooleanField(default=False)
