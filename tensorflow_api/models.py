from django.db import models

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    language = models.CharField(max_length=10, default="en")  # Add language field
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    original_text_provided = models.BooleanField(default=True)  # New field
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='questions',
        default=1  # Default to Topic with ID=1
    )

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="option_images/", blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    original_text_provided = models.BooleanField(default=True)  # New field

    def __str__(self):
        return self.text if self.text else "Image Option"


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.question.text}"

class Translation(models.Model):
    original_text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)
    is_ai_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source_language} -> {self.target_language}: {self.original_text[:50]}"


