from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('upload/', views.upload_factura, name='upload_factura'), 
path('generate-mobile-link/', views.generate_mobile_upload_link, name='generate_mobile_link'),
path('mobile-upload/', views.mobile_upload, name='mobile_upload'),
]

# Servir archivos de medios durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
