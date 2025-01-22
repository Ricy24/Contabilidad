# analisis/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.db.models import Sum
from datetime import datetime, timedelta
from main.models import Empleado, RegistroHoras, ImpuestosMensuales
from ventas.models import Venta, DetalleVenta
from inventario.models import CompraFactura, Producto
from .models import ReporteFinanciero

@login_required
def dashboard_analisis(request):
    # Obtener fechas para filtrado
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Análisis de ventas
    ventas_data = Venta.objects.filter(
        fecha__date__range=[fecha_inicio, fecha_fin]
    ).aggregate(
        total_ventas=Sum('subtotal'),
        cantidad_ventas=Count('id'),
        promedio_venta=Avg('subtotal')
    )

    # Análisis de compras
    compras_data = CompraFactura.objects.filter(
        fecha__date__range=[fecha_inicio, fecha_fin]
    ).aggregate(
        total_compras=Sum('total'),
        cantidad_compras=Count('id'),
        promedio_compra=Avg('total')
    )

    # Análisis de nómina
    nomina_data = RegistroHoras.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).aggregate(
        total_pagos=Sum('pago_calculado'),
        horas_trabajadas=Sum('horas_trabajadas')
    )

    # Productos más vendidos
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date__range=[fecha_inicio, fecha_fin]
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingresos_total=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-cantidad_total')[:10]

    # Calcular utilidad
    ingresos = ventas_data['total_ventas'] or Decimal('0')
    gastos_compras = compras_data['total_compras'] or Decimal('0')
    gastos_nomina = nomina_data['total_pagos'] or Decimal('0')
    utilidad = ingresos - (gastos_compras + gastos_nomina)

    context = {
        'ventas_data': ventas_data,
        'compras_data': compras_data,
        'nomina_data': nomina_data,
        'productos_vendidos': productos_vendidos,
        'utilidad': utilidad,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'analisis/dashboard_analisis.html', context)
def decimal_or_zero(value):
    """Convierte un valor a Decimal de forma segura"""
    try:
        if value is None or value == '':
            return Decimal('0.00')
        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except:
        return Decimal('0.00')

@login_required
def reporte_financiero(request):
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    if request.method == 'POST':
        try:
            fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
        except:
            fecha_fin = datetime.now().date()
            fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Obtener reportes existentes
    reporte = ReporteFinanciero.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).order_by('-fecha')
    
    # Crear reportes faltantes
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        try:
            # Verificar si ya existe el reporte para esta fecha
            if not ReporteFinanciero.objects.filter(fecha=fecha_actual).exists():
                # Calcular totales del día
                ventas_total = decimal_or_zero(
                    Venta.objects.filter(fecha__date=fecha_actual)
                    .aggregate(total=Sum('subtotal'))['total']
                )
                
                compras_total = decimal_or_zero(
                    CompraFactura.objects.filter(fecha__date=fecha_actual)
                    .aggregate(total=Sum('total'))['total']
                )
                
                nomina_total = decimal_or_zero(
                    RegistroHoras.objects.filter(fecha__date=fecha_actual)
                    .aggregate(total=Sum('pago_calculado'))['total']
                )
                
                # Crear nuevo reporte
                nuevo_reporte = ReporteFinanciero(
                    fecha=fecha_actual,
                    ingresos_ventas=ventas_total,
                    costos_compras=compras_total,
                    costos_nomina=nomina_total
                )
                nuevo_reporte.calcular_utilidad()
                nuevo_reporte.save()
                
        except Exception as e:
            print(f"Error al procesar fecha {fecha_actual}: {str(e)}")
        
        fecha_actual += timedelta(days=1)
    
    # Recargar reportes después de crear los faltantes
    reporte = ReporteFinanciero.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).order_by('-fecha')
    
    # Calcular totales
    try:
        totales = {
            'ingresos_totales': decimal_or_zero(
                reporte.aggregate(total=Sum('ingresos_ventas'))['total']
            ),
            'costos_compras_totales': decimal_or_zero(
                reporte.aggregate(total=Sum('costos_compras'))['total']
            ),
            'costos_nomina_totales': decimal_or_zero(
                reporte.aggregate(total=Sum('costos_nomina'))['total']
            ),
            'utilidad_bruta_total': decimal_or_zero(
                reporte.aggregate(total=Sum('utilidad_bruta'))['total']
            )
        }
        
        ingresos = decimal_or_zero(totales['ingresos_totales'])
        if ingresos > 0:
            totales['margen_utilidad_total'] = (
                (decimal_or_zero(totales['utilidad_bruta_total']) / ingresos) * 100
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            totales['margen_utilidad_total'] = Decimal('0.00')
            
    except Exception as e:
        print(f"Error al calcular totales: {str(e)}")
        totales = {
            'ingresos_totales': Decimal('0.00'),
            'costos_compras_totales': Decimal('0.00'),
            'costos_nomina_totales': Decimal('0.00'),
            'utilidad_bruta_total': Decimal('0.00'),
            'margen_utilidad_total': Decimal('0.00')
        }
    
    context = {
        'reportes': reporte,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'totales': totales
    }
    
    return render(request, 'analisis/reporte_financiero.html', context)