from django.urls import path
from . import views


urlpatterns = [
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/registrar/', views.registrar_venta, name='registrar_venta'),
    path('factura/<int:factura_id>/', views.ver_factura, name='ver_factura'),
    path('ventas/extracto/', views.ventas_por_periodo, name='ventas_extracto'),
path('ventas/dia/', views.ventas_por_dia, name='ventas_dia'),
path('ventas/exportar/', views.exportar_extracto, name='exportar_extracto'),
]

