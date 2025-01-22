from django.urls import path
from . import views

urlpatterns = [
    # Ruta para el dashboard principal
    path('', views.dashboard, name='dashboard'),
    path('configuracion/', views.configuracion, name='configuracion'),
    
    # Rutas para manejo de turnos
    path('empleado/<int:empleado_id>/iniciar-turno/', 
         views.iniciar_turno_empleado, 
         name='iniciar_turno_empleado'),
    
    path('empleado/<int:empleado_id>/finalizar-turno/', 
         views.finalizar_turno_empleado, 
         name='finalizar_turno_empleado'),
    
    # Rutas para reportes de horas/días trabajados
    path('horas-trabajadas/', 
         views.horas_trabajadas, 
         name='horas_trabajadas'),
    
    path('empleado/<int:empleado_id>/detalle-horas/', 
         views.detalle_empleado_horas, 
         name='detalle_empleado_horas'),
         
]


    


    