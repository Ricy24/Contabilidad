from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Cliente, Venta, DetalleVenta, Factura
from inventario.models import Producto
from django.utils.timezone import now
from django.db.models import Sum, Count,  DecimalField
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from datetime import datetime, timedelta
import uuid
from decimal import Decimal
from django.db.models import Sum, F
from django.db.models.functions import Cast



def lista_ventas(request):
    # Get filter parameters from request
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    periodo = request.GET.get('periodo', 'diario')  # diario, semanal, mensual, anual

    # Base queryset
    ventas = Venta.objects.all()

    # Apply date filters if provided
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ventas = ventas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        ventas = ventas.filter(fecha__lte=fecha_fin)

    # Group by period
    if periodo == 'diario':
        ventas = ventas.annotate(periodo_fecha=TruncDate('fecha'))
    elif periodo == 'semanal':
        ventas = ventas.annotate(periodo_fecha=TruncWeek('fecha'))
    elif periodo == 'mensual':
        ventas = ventas.annotate(periodo_fecha=TruncMonth('fecha'))
    elif periodo == 'anual':
        ventas = ventas.annotate(periodo_fecha=TruncYear('fecha'))

    # Aggregate sales data
    ventas_agrupadas = ventas.values('periodo_fecha').annotate(
        total_ventas=Sum('subtotal'),
        cantidad_ventas=Count('id')
    ).order_by('-periodo_fecha')

    # Get analytics data if detailed view is requested
    if request.GET.get('view_type') == 'detallado':
        # Get top selling products
        productos_mas_vendidos = DetalleVenta.objects.filter(
            venta__in=ventas
        ).values('producto__nombre').annotate(
            total_vendido=Sum('cantidad'),
           total_ingresos=Sum(Cast('precio_unitario', DecimalField()) * F('cantidad'))

        ).order_by('-total_vendido')[:10]

        # Calculate total statistics
        estadisticas = {
            'total_ingresos': ventas.aggregate(Sum('subtotal'))['subtotal__sum'] or 0,
            'total_ventas': ventas.count(),
            'promedio_venta': (ventas.aggregate(Sum('subtotal'))['subtotal__sum'] or 0) / (ventas.count() or 1),
        }

        context = {
            'ventas_agrupadas': ventas_agrupadas,
            'productos_mas_vendidos': productos_mas_vendidos,
            'estadisticas': estadisticas,
            'periodo': periodo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'template': 'ventas/ventas_detallado.html'
        }
    else:
        context = {
            'ventas': ventas.order_by('-fecha'),
            'ventas_agrupadas': ventas_agrupadas,
            'periodo': periodo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'template': 'ventas/lista_ventas.html'
        }

    return render(request, context['template'], context)

def registrar_venta(request):
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        # Obtener las listas de productos y cantidades
        producto_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')
        
        # Inicializar el total de la venta
        total_venta = Decimal('0.0')
        
        # Crear la venta inicial con el primer producto
        if producto_ids and cantidades:
            primer_producto = get_object_or_404(Producto, id=producto_ids[0])
            primera_cantidad = int(cantidades[0])
            primer_precio = Decimal(primer_producto.precio)
            primer_subtotal = primera_cantidad * primer_precio
            
            venta = Venta.objects.create(
                producto=primer_producto.nombre,  # Mantenemos este campo por compatibilidad
                cantidad=primera_cantidad,        # Mantenemos este campo por compatibilidad
                precio_unitario=primer_precio,    # Mantenemos este campo por compatibilidad
                subtotal=primer_subtotal         # Mantenemos este campo por compatibilidad
            )
            
            # Crear el detalle de venta para el primer producto
            DetalleVenta.objects.create(
                venta=venta,
                producto=primer_producto,
                cantidad=primera_cantidad,
                precio_unitario=primer_precio
            )
            
            total_venta += primer_subtotal
            
            # Procesar los productos adicionales si existen
            for producto_id, cantidad in zip(producto_ids[1:], cantidades[1:]):
                if producto_id and int(cantidad) > 0:
                    producto = get_object_or_404(Producto, id=producto_id)
                    cantidad = int(cantidad)
                    precio_unitario = Decimal(producto.precio)
                    subtotal = cantidad * precio_unitario
                    
                    # Crear detalle de venta para cada producto adicional
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario
                    )
                    
                    total_venta += subtotal
            
            # Actualizar el total de la venta
            venta.subtotal = total_venta
            venta.save()

            # Procesar la factura si se solicita
            generar_factura = request.POST.get('generar_factura', None)
            if generar_factura:
                numero_factura = str(uuid.uuid4())[:8]
                nombre_cliente = request.POST.get('nombre_cliente')

                if nombre_cliente:
                    cliente_temp = Cliente.objects.create(
                        nombre=nombre_cliente,
                        es_temporal=True
                    )

                    factura = Factura.objects.create(
                        venta=venta,
                        cliente=cliente_temp,
                        numero_factura=numero_factura,
                    )
                    
                    return redirect('ver_factura', factura_id=factura.id)

            return redirect('lista_ventas')

    return render(request, 'ventas/registrar_venta.html', {
        'productos': productos,
    })

    
def ver_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    # Obtener todos los detalles de la venta
    detalles_venta = DetalleVenta.objects.filter(venta=factura.venta)
    
    context = {
        'factura': factura,
        'venta': factura.venta,
        'cliente': factura.cliente,
        'detalles_venta': detalles_venta,  # Agregamos los detalles de la venta al contexto
        'restaurante': {
            'nombre': 'LA CASA DEL SABOR BOYACENSE LAS MAIRAS',
            'nit': '1055332740-8',
            'direccion': 'CARRERA 8B 58 18',
            'telefono': '3138616657',
            'libre': 'Factura libre de IVA',
        }
    }
    return render(request, 'ventas/factura.html', context)


    from django.db.models import Sum, F
from django.utils import timezone
from datetime import datetime, timedelta

def ventas_por_periodo(request):
    periodo = request.GET.get('periodo', 'diario')
    fecha_actual = timezone.now()
    
    # Configurar fechas según el periodo
    if periodo == 'diario':
        fecha_inicio = fecha_actual.replace(hour=0, minute=0, second=0)
        fecha_fin = fecha_actual.replace(hour=23, minute=59, second=59)
    elif periodo == 'semanal':
        fecha_inicio = fecha_actual - timedelta(days=fecha_actual.weekday())
        fecha_fin = fecha_inicio + timedelta(days=6)
    elif periodo == 'mensual':
        fecha_inicio = fecha_actual.replace(day=1, hour=0, minute=0, second=0)
        fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif periodo == 'anual':
        fecha_inicio = fecha_actual.replace(month=1, day=1, hour=0, minute=0, second=0)
        fecha_fin = fecha_actual.replace(month=12, day=31, hour=23, minute=59, second=59)
    else:
        fecha_inicio = fecha_actual
        fecha_fin = fecha_actual

    # Obtener ventas del periodo
    ventas = Venta.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).order_by('-fecha')

    # Calcular totales
    total_periodo = ventas.aggregate(
        total_ventas=Sum('subtotal'),
        total_productos=Sum(F('detalleventa__cantidad'))
    )

    context = {
        'ventas': ventas,
        'periodo': periodo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_ventas': total_periodo['total_ventas'] or 0,
        'total_productos': total_periodo['total_productos'] or 0
    }
    
    return render(request, 'ventas/extracto_ventas.html', context)

def ventas_por_dia(request):
    fecha = request.GET.get('fecha', timezone.now().date())
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    ventas = Venta.objects.filter(
        fecha__date=fecha
    ).order_by('-fecha')
    
    total_dia = ventas.aggregate(
        total_ventas=Sum('subtotal'),
        total_productos=Sum(F('detalleventa__cantidad'))
    )
    
    context = {
        'ventas': ventas,
        'fecha': fecha,
        'total_ventas': total_dia['total_ventas'] or 0,
        'total_productos': total_dia['total_productos'] or 0
    }
    
    return render(request, 'ventas/ventas_dia.html', context)

def exportar_extracto(request):
    periodo = request.GET.get('periodo', 'diario')
    formato = request.GET.get('formato', 'pdf')
    
    # Obtener las ventas usando la función existente
    response = ventas_por_periodo(request)
    context = response.context_data
    
    if formato == 'pdf':
        # Crear PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="extracto_{periodo}.pdf"'
        
        # Aquí agregarías la lógica para generar el PDF
        # Puedes usar reportlab o weasyprint
        
    elif formato == 'excel':
        import xlsxwriter
        from io import BytesIO
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Encabezados
        headers = ['Fecha', 'Productos', 'Total']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Datos
        for row, venta in enumerate(context['ventas'], start=1):
            worksheet.write(row, 0, venta.fecha.strftime('%Y-%m-%d %H:%M'))
            worksheet.write(row, 1, venta.producto)
            worksheet.write(row, 2, float(venta.subtotal))
        
        workbook.close()
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="extracto_{periodo}.xlsx"'
        
    return response

    
# Add new helper function for analytics
def obtener_estadisticas_ventas(ventas_queryset):
    """
    Calculate detailed sales statistics for a given queryset
    """
    return {
        'total_ingresos': ventas_queryset.aggregate(Sum('subtotal'))['subtotal__sum'] or 0,
        'total_ventas': ventas_queryset.count(),
        'productos_vendidos': DetalleVenta.objects.filter(
            venta__in=ventas_queryset
        ).aggregate(Sum('cantidad'))['cantidad__sum'] or 0,
        'promedio_venta': (
            ventas_queryset.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        ) / (ventas_queryset.count() or 1),
    }