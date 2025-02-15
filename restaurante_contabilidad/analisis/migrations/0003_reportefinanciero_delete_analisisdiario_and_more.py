# Generated by Django 5.1.4 on 2025-01-13 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analisis', '0002_configuraciontelegram'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteFinanciero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('ingresos_ventas', models.DecimalField(decimal_places=2, max_digits=12)),
                ('costos_compras', models.DecimalField(decimal_places=2, max_digits=12)),
                ('costos_nomina', models.DecimalField(decimal_places=2, max_digits=12)),
                ('utilidad_bruta', models.DecimalField(decimal_places=2, max_digits=12)),
                ('margen_utilidad', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.DeleteModel(
            name='AnalisisDiario',
        ),
        migrations.DeleteModel(
            name='ConfiguracionTelegram',
        ),
        migrations.DeleteModel(
            name='Impuesto',
        ),
    ]
