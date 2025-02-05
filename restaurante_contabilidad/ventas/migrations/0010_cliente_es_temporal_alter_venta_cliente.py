# Generated by Django 5.1.4 on 2025-01-03 19:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0009_venta_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='es_temporal',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ventas.cliente'),
        ),
    ]
