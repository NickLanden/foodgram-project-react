# Generated by Django 2.2.19 on 2022-08-06 18:33

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(blank=True, default=None, image_field=None, max_length=18, null=True, samples=None, unique=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True),
        ),
    ]
