# Generated by Django 5.1.4 on 2025-01-03 18:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0008_rename_total_venta_precio_unitario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
