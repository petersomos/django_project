from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Question, Option, Topic, Translation


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")  # Fields to display
    search_fields = ("name",)  # Searchable by name

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('text', 'created_at', 'image_preview', 'topic')  # Use 'topic' instead of 'topic__name'
    search_fields = ('text', 'topic__name')  # Corrected search_fields tuple
    list_filter = ('topic',)  # Add filter by topic
    autocomplete_fields = ('topic',) 
    readonly_fields = ('image_preview',)
    ordering = ("id",)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;"/>')
        return "No Image"

    image_preview.short_description = 'Image Preview'

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_correct', 'question')

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("id", "source_language", "target_language", "original_text", "translated_text", "is_ai_generated")
    list_filter = ("source_language", "target_language", "is_ai_generated")
    search_fields = ("original_text", "translated_text")
