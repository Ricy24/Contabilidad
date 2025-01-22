from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import Producto, CompraFactura
from .forms import ProductoForm 
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from django.conf import settings
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from telegram import Bot, Update
from telegram.ext import CallbackContext
from django.core.files.base import ContentFile
import urllib
from .models import CompraFactura
import pyngrok.ngrok as ngrok


@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    compras = CompraFactura.objects.all().order_by('-fecha')
    return render(request, 'inventario/lista_productos.html', {
        'productos': productos,
        'compras': compras
    })

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/editar_producto.html', {'form': form, 'producto': producto})

@login_required
def lista_compras(request):
    compras = CompraFactura.objects.all().order_by('-fecha')
    estadisticas = CompraFactura.get_estadisticas()
    return render(request, 'inventario/lista_compras.html', {
        'compras': compras,
        'estadisticas': estadisticas
    })

@login_required
def upload_factura(request):
    if request.method == "POST":
        try:
            imagen = request.FILES.get('imagen')
            total = float(request.POST.get('total', 0))
            
            if not imagen:
                return JsonResponse({"error": "No se proporcionó imagen"}, status=400)
            
            compra = CompraFactura.objects.create(
                total=total,
                imagen=imagen
            )
            
            return JsonResponse({
                "status": "success",
                "message": f"Factura #{compra.id} registrada exitosamente"
            })
        except Exception as e:
            logging.error(f"Error al subir factura: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return render(request, 'inventario/upload_factura.html')

@login_required
def generate_mobile_upload_link(request):
    try:
        # Iniciar túnel ngrok
        public_url = ngrok.connect(8000)
        upload_url = f"{public_url}/inventario/mobile-upload/"
        
        # Número de WhatsApp configurado (puedes ponerlo en settings.py)
        WHATSAPP_NUMBER = "313 8616657"  # Reemplaza con tu número
        
        # Crear mensaje para WhatsApp
        mensaje = f"Por favor sube tu factura en el siguiente enlace: {upload_url}"
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(mensaje)}"
        
        return JsonResponse({
            "status": "success",
            "upload_url": upload_url,
            "whatsapp_url": whatsapp_url
        })
    except Exception as e:
        logging.error(f"Error generando enlace: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def mobile_upload(request):
    if request.method == "POST":
        try:
            imagen = request.FILES.get('imagen')
            total = float(request.POST.get('total', 0))
            
            if not imagen:
                return JsonResponse({"error": "No se proporcionó imagen"}, status=400)
            
            compra = CompraFactura.objects.create(
                total=total,
                imagen=imagen
            )
            
            return JsonResponse({
                "status": "success",
                "message": f"Factura #{compra.id} registrada exitosamente"
            })
        except Exception as e:
            logging.error(f"Error al subir factura móvil: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return render(request, 'inventario/mobile_upload.html')

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            data = json.loads(request.body)
            update = Update.de_json(data, bot)
            
            message = update.message
            if message.photo:
                file = bot.get_file(message.photo[-1].file_id)
                total = float(message.caption) if message.caption else 0
                
                imagen_bytes = file.download_as_bytearray()
                
                compra = CompraFactura.objects.create(
                    total=total,
                    telegram_message_id=message.message_id,
                    chat_id=message.chat_id
                )
                
                compra.imagen.save(
                    f'factura_{compra.fecha.strftime("%Y%m%d_%H%M%S")}.jpg',
                    ContentFile(imagen_bytes)
                )
                
                bot.send_message(
                    chat_id=message.chat_id,
                    text=f"Factura #{compra.id} registrada exitosamente"
                )
            else:
                bot.send_message(
                    chat_id=message.chat_id,
                    text="Por favor envía una imagen de la factura con el total en el caption"
                )
            
            return JsonResponse({"status": "Factura procesada exitosamente"})
        except Exception as e:
            logging.error(f"Error procesando factura: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)