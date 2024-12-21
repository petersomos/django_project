import requests
from django.core.management.base import BaseCommand
from tensorflow_api.models import Question, Option, Translation

class Command(BaseCommand):
    help = "Populate translations for all questions and options using the translation API."

    def add_arguments(self, parser):
        parser.add_argument(
            '--forceAll',
            action='store_true',
            help="Force re-translation and overwrite all existing translations.",
        )

    def handle(self, *args, **options):
        supported_languages = ["en", "de", "fr", "hu", "sk"]
        force_all = options['forceAll']
        api_url = "http://192.168.1.130:5000/translate"  # Local translation API URL

        def translate_text(original_text, source_language, target_language):
            """Call the API to translate text."""
            try:
                response = requests.post(api_url, json={
                    "text": original_text,
                    "source_language": source_language,
                    "target_language": target_language,
                })
                if response.status_code == 200:
                    return response.json().get("translated_text", original_text)
                else:
                    self.stderr.write(f"API error: {response.text}")
                    return original_text
            except Exception as e:
                self.stderr.write(f"Failed to call API: {str(e)}")
                return original_text

        # Translate questions
        for question in Question.objects.all():
            for target_language in supported_languages:
                if question.language != target_language:
                    translation, created = Translation.objects.get_or_create(
                        original_text=question.text,
                        source_language=question.language,
                        target_language=target_language,
                    )
                    if force_all or created or not translation.translated_text:
                        translated_text = translate_text(
                            question.text, question.language, target_language
                        )
                        translation.translated_text = translated_text
                        translation.save()
                        self.stdout.write(
                            f"Translated question '{question.text}' to '{target_language}': {translated_text}"
                        )

        # Translate options
        for option in Option.objects.select_related('question').all():
            source_language = option.question.language
            for target_language in supported_languages:
                if source_language != target_language:
                    translation, created = Translation.objects.get_or_create(
                        original_text=option.text,
                        source_language=source_language,
                        target_language=target_language,
                    )
                    if force_all or created or not translation.translated_text:
                        translated_text = translate_text(
                            option.text, source_language, target_language
                        )
                        translation.translated_text = translated_text
                        translation.save()
                        self.stdout.write(
                            f"Translated option '{option.text}' to '{target_language}': {translated_text}"
                        )

        self.stdout.write(self.style.SUCCESS(
            "Translations populated successfully!" +
            (" (Force re-translation enabled.)" if force_all else "")
        ))
