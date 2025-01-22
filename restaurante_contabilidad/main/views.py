from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from random import choice
from calendar import monthrange
from django.db.models import Sum, Count 

from .models import Configuracion, Empleado, RegistroHoras, ImpuestosMensuales
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto
from django.contrib import messages



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Empleado, RegistroHoras
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from random import choice

from .models import Configuracion, Empleado, RegistroHoras, ImpuestosMensuales
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Empleado, RegistroHoras
from django.utils import timezone


FRASES_MOTIVACIONALES = [
    "¡El éxito es la suma de pequeños esfuerzos repetidos día tras día!",
    "La excelencia no es un acto, sino un hábito.",
    "Cada plato que servimos es una oportunidad para hacer feliz a alguien.",
    "La calidad es la mejor receta para el éxito."
]


@login_required
def dashboard(request):
    hoy = date.today()

    # Datos principales de ventas
    ventas_hoy = Venta.objects.filter(fecha__date=hoy).count()
    ventas_ayer = Venta.objects.filter(fecha__date=hoy - timedelta(days=1)).count()

    # Cálculo del ingreso total del día
    ingreso_total_hoy = Venta.objects.filter(fecha__date=hoy).aggregate(
        total=Sum(F('detalleventa__cantidad') * F('detalleventa__precio_unitario'))
    )['total'] or 0

    # Impuestos del mes
    primer_dia_mes = hoy.replace(day=1)
    ventas_mes = Venta.objects.filter(
        fecha__date__gte=primer_dia_mes,
        fecha__date__lte=hoy
    ).annotate(total=Sum(F('detalleventa__cantidad') * F('detalleventa__precio_unitario'))).aggregate(total=Sum('total'))['total'] or 0

    iva = ventas_mes * Decimal('0.19')
    retencion = ventas_mes * Decimal('0.025')
    ica = ventas_mes * Decimal('0.007')

    impuestos, _ = ImpuestosMensuales.objects.get_or_create(
        fecha=primer_dia_mes,
        defaults={
            'ventas_totales': ventas_mes,
            'iva_generado': iva,
            'retencion_fuente': retencion,
            'ica': ica
        }
    )

    # Productos más vendidos
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date=hoy
    ).values('producto__nombre').annotate(total=Sum('cantidad')).order_by('-total')[:5]

    # Datos de empleados
    empleados = Empleado.objects.all()
    turnos_activos = RegistroHoras.objects.filter(
        hora_fin__isnull=True
    ).select_related('empleado')
    
    turnos_dict = {
        turno.empleado.id: turno for turno in turnos_activos
    }

    # Frase motivacional
    frase_motivacional = choice(FRASES_MOTIVACIONALES)

    context = {
        'fecha_actual': hoy,
        'ventas_hoy': ventas_hoy,
        'ventas_ayer': ventas_ayer,
        'ingreso_total_hoy': ingreso_total_hoy,
        'productos_mas_vendidos': productos_mas_vendidos,
        'impuestos_mes': impuestos,
        'frase_motivacional': frase_motivacional,
        'empleados': empleados,
        'turnos_activos': turnos_dict,
    }

    return render(request, 'main/dashboard.html', context)

@login_required
def iniciar_turno_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    turno_activo = RegistroHoras.objects.filter(
        empleado=empleado,
        hora_fin__isnull=True
    ).first()
    
    if turno_activo:
        messages.error(request, f'El empleado {empleado.nombre} ya tiene un turno activo')
    else:
        turno = empleado.iniciar_turno()
        messages.success(request, f'Turno iniciado para {empleado.nombre}')
    
    return redirect('dashboard')

@login_required
def finalizar_turno_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    turno_activo = RegistroHoras.objects.filter(
        empleado=empleado,
        hora_fin__isnull=True
    ).first()
    
    if turno_activo:
        # Calculamos la duración del turno antes de finalizarlo
        duracion = timezone.now() - turno_activo.hora_inicio
        horas_trabajadas = duracion.total_seconds() / 3600  # Convertir a horas
        
        turno = empleado.finalizar_turno(turno_activo.id)
        
        # Formatear las fechas
        hora_inicio_formateada = turno.hora_inicio.strftime("%H:%M")
        hora_fin_formateada = turno.hora_fin.strftime("%H:%M")
        
        # Mensaje más detallado
        messages.success(
            request, 
            f'Turno finalizado para {empleado.nombre}\n'
            f'Inicio: {hora_inicio_formateada}\n'
            f'Fin: {hora_fin_formateada}\n'
            f'Duración: {horas_trabajadas:.2f} horas\n'
            f'Pago: ${turno.pago_calculado:.2f}'
        )
    else:
        messages.error(request, f'El empleado {empleado.nombre} no tiene un turno activo')
    
    return redirect('dashboard')

@login_required
def horas_trabajadas(request):
    # Obtener parámetros de filtro
    empleado_id = request.GET.get('empleado')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    # Configurar fechas por defecto (mes actual)
    hoy = timezone.now()
    primer_dia_mes = hoy.replace(day=1)
    ultimo_dia_mes = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])  # Aquí usamos monthrange
    
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date() if fecha_inicio_str else primer_dia_mes
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() if fecha_fin_str else ultimo_dia_mes

    # Query base
    registros = RegistroHoras.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin],
        hora_fin__isnull=False
    ).select_related('empleado')

    # Filtrar por empleado si se especifica
    if empleado_id:
        registros = registros.filter(empleado_id=empleado_id)

    # Obtener resumen por empleado

    resumen_empleados = registros.values(
        'empleado__id',
        'empleado__nombre',
        'empleado__cargo'
    ).annotate(
        total_horas=Count('fecha', distinct=True),  # Ahora cuenta días únicos
        total_pago=Sum('pago_calculado'),
        dias_trabajados=Count('fecha', distinct=True)
    )
    
    # Obtener todos los empleados para el filtro
    empleados = Empleado.objects.filter(activo=True)

    context = {
        'empleados': empleados,
        'resumen_empleados': resumen_empleados,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'empleado_seleccionado': empleado_id,
        'registros': registros
    }
    
    return render(request, 'main/horas_trabajadas.html', context)

@login_required
def detalle_empleado_horas(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    # Fechas por defecto (mes actual)
    hoy = timezone.now()
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date() if fecha_inicio_str else hoy.replace(day=1)
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() if fecha_fin_str else hoy

    registros = RegistroHoras.objects.filter(
        empleado=empleado,
        fecha__range=[fecha_inicio, fecha_fin],
        hora_fin__isnull=False
    ).order_by('-fecha', '-hora_inicio')

    context = {
        'empleado': empleado,
        'registros': registros,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_horas': registros.count(),  #son dias trabajadps
        'total_pago': registros.aggregate(total=Sum('pago_calculado'))['total'] or 0
    }
    
    return render(request, 'main/detalle_horas_empleado.html', context)

@login_required
def configuracion(request):
    config, created = Configuracion.objects.get_or_create(pk=1)

    if request.method == 'POST':
        config.nombre_restaurante = request.POST.get('nombre_restaurante', config.nombre_restaurante)
        config.nit = request.POST.get('nit', config.nit)
        config.direccion = request.POST.get('direccion', config.direccion)
        config.telefono = request.POST.get('telefono', config.telefono)
        config.email = request.POST.get('email', config.email)



        config.save()
        return redirect('dashboard')

    return render(request, 'main/configuracion.html', {'config': config})
