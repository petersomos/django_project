# Generated by Django 5.1.4 on 2024-12-19 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tensorflow_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
    ]
