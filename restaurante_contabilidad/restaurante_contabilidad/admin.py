from django.contrib import admin
from .models import AccountEmailAddress, InventarioCompra  # Importa los modelos que quieras gestionar

admin.site.register(AccountEmailAddress)
admin.site.register(InventarioCompra)
