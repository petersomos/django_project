# Generated by Django 5.1.4 on 2024-12-21 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tensorflow_api', '0007_alter_translation_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='translation',
            name='is_ai_generated',
            field=models.BooleanField(default=True),
        ),
    ]
