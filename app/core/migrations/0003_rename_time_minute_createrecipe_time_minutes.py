# Generated by Django 4.0.10 on 2024-11-15 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_createrecipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='createrecipe',
            old_name='time_minute',
            new_name='time_minutes',
        ),
    ]
