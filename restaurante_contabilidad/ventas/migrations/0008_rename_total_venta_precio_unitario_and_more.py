# Generated by Django 5.1.4 on 2025-01-03 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0007_remove_factura_numero_factura_cliente_venta_cliente_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='venta',
            old_name='total',
            new_name='precio_unitario',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='fecha',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='pagado',
        ),
        migrations.AddField(
            model_name='venta',
            name='cantidad',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='producto',
            field=models.CharField(default='Producto genérico', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ventas.cliente'),
        ),
    ]
