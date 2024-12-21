from django.db import migrations, models

def create_default_topic(apps, schema_editor):
    Topic = apps.get_model('tensorflow_api', 'Topic')  # Use apps.get_model to fetch Topic dynamically
    Topic.objects.get_or_create(
        id=1, 
        defaults={
            "name": "Default Topic",
            "description": "Default topic for migration purposes."
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('tensorflow_api', '0008_translation_is_ai_generated'),  # Correct dependency
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(default=1, on_delete=models.CASCADE, related_name='questions', to='tensorflow_api.Topic'),
        ),
        migrations.RunPython(create_default_topic),  # This ensures the default topic is created
    ]
