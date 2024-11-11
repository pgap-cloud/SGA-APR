# Generated by Django 4.2.7 on 2024-11-11 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.CharField(choices=[('ADMIN', 'Administrador'), ('SECRETARIA', 'Secretaria'), ('USUARIO', 'Usuario')], default='USUARIO', max_length=20),
        ),
    ]
