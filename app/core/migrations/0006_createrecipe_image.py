# Generated by Django 4.0.10 on 2024-12-01 15:30

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_ingredient_createrecipe_ingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='createrecipe',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.recipe_image_file_path),
        ),
    ]
