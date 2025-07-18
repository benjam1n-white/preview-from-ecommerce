# Generated by Django 3.2.12 on 2025-06-10 18:25

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name'], 'verbose_name': 'producto', 'verbose_name_plural': 'productos'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'perfil', 'verbose_name_plural': 'perfiles'},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['name'], 'verbose_name': 'tienda', 'verbose_name_plural': 'tiendas'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'usuario', 'verbose_name_plural': 'usuarios'},
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='precio'),
        ),
        migrations.AlterField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.store', verbose_name='tienda'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('CL', 'Cliente'), ('SL', 'Vendedor'), ('AD', 'Administrador')], default='CL', max_length=2, verbose_name='rol'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='usuario'),
        ),
        migrations.AlterField(
            model_name='store',
            name='address',
            field=models.CharField(max_length=200, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=100, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='store',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stores', to=settings.AUTH_USER_MODEL, verbose_name='dueño'),
        ),
    ]
