# Generated by Django 5.1.4 on 2025-01-12 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_rename_salario_por_hora_empleado_salario_por_dia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrohoras',
            name='hora_fin',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registrohoras',
            name='hora_inicio',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
