# Generated by Django 5.1.4 on 2025-01-03 23:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0011_alter_detalleventa_options_alter_factura_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detalleventa',
            options={},
        ),
        migrations.AlterModelOptions(
            name='factura',
            options={},
        ),
        migrations.AlterModelOptions(
            name='venta',
            options={},
        ),
        migrations.RemoveField(
            model_name='detalleventa',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='total',
        ),
        migrations.AddField(
            model_name='venta',
            name='cantidad',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='precio_unitario',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='producto',
            field=models.CharField(default="Desayuno", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='factura',
            name='imagen',
            field=models.ImageField(default='media/imagenes', upload_to='facturas/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='factura',
            name='numero_factura',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='factura',
            name='venta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.venta'),
        ),
    ]
