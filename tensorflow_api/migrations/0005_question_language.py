# Generated by Django 5.1.4 on 2024-12-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tensorflow_api', '0004_remove_question_language_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='language',
            field=models.CharField(default='en', max_length=10),
        ),
    ]
