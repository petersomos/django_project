from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import logging
from django.shortcuts import render
from .models import Question, Option, Response, Translation
import os
from PIL import Image, ImageDraw
from .utils import translate_text_if_needed
 

# Configure logging
logger = logging.getLogger(__name__)

TRANSLATION_SERVICE_URL = "http://192.168.1.130:5000/translate"

KNOWN_TRANSLATIONS = {
    "de": {
        "Ja": "Yes",
        "Nein": "No",
    },
    "en": {
        "Yes": "Ja",
        "No": "Nein",
    }
    
}

def issue_badge(user, score):
    """Generate a badge for users who pass the quiz."""
    if score >= 70:  # Example: 70% passing threshold
        badge_path = f"media/badges/{user.username}_badge.png"
        os.makedirs(os.path.dirname(badge_path), exist_ok=True)

        # Generate badge image
        badge = Image.new("RGB", (300, 300), color="gold")
        draw = ImageDraw.Draw(badge)
        draw.text((50, 150), "Certified in Statistics", fill="black")
        badge.save(badge_path)

        logger.info(f"Badge generated for user {user.username} at {badge_path}")
        return badge_path
    return None

# Helper function to translate text using the external servicedef translate_text_if_needed(text, source_language, target_language):
def translate_text_if_needed(text, source_language, target_language):
    try:
        # If source and target languages are the same, skip translation
        if source_language == target_language:
            logger.debug(f"No translation needed for text: '{text}'")
            return text, False

        # Handle known translations for specific cases
        KNOWN_TRANSLATIONS = {
            "de": {"Ja": "Yes", "Nein": "No"},
            "en": {"Yes": "Ja", "No": "Nein"}
        }
        if text in KNOWN_TRANSLATIONS.get(source_language, {}):
            logger.debug(f"Using known translation for text: '{text}'")
            return KNOWN_TRANSLATIONS[source_language][text], False

        # Log the translation request
        logger.debug(f"Attempting to translate from {source_language} to {target_language}: '{text}'")

        # Prepare payload and make request to translation service
        response = requests.post(TRANSLATION_SERVICE_URL, json={
            "text": text,
            "source_language": source_language,
            "target_language": target_language
        })

        # Ensure response is processed as JSON
        response_data = response.json()

        # Handle successful responses
        if response.status_code == 200:
            translated_text = response_data.get("translated_text", text)
            if not translated_text or len(translated_text) > 500:  # Avoid nonsensical or excessively long translations
                logger.warning(f"Translation service returned invalid response. Using original text: '{text}'")
                return text, True

            is_ai_generated = response_data.get("is_ai_generated", True)
            logger.debug(f"Translation successful. Text: '{translated_text}' | AI Generated: {is_ai_generated}")
            return translated_text, is_ai_generated

        # Handle errors from the translation service
        else:
            error_message = response_data.get("error", "Unknown error")
            logger.error(f"Translation service failed with status {response.status_code}: {error_message}")
            return text, True  # Return the original text if translation fails

    # Catch any unexpected exceptions and log them
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error while connecting to translation service: {req_err}")
    except json.JSONDecodeError as json_err:
        logger.error(f"Error decoding JSON from translation service: {json_err}")
    except Exception as e:
        logger.error(f"Unexpected error during translation: {e}")

    # Return original text and flag as AI-generated in case of any failure
    return text, True



@csrf_exempt
def translate_text_view(request):
    """
    Handle translation requests via POST.
    """
    if request.method == "POST":
        try:
            # Parse incoming JSON
            data = json.loads(request.body)
            text = data.get("text")
            source_language = data.get("source_language", "en")
            target_language = data.get("target_language", "en")

            # Validate inputs
            if not text:
                return JsonResponse({"error": "No text provided"}, status=400)
            if not source_language or not target_language:
                return JsonResponse({"error": "Source or target language missing"}, status=400)

            # Log incoming data for debugging
            logger.info(f"Translating text: {text} | From: {source_language} | To: {target_language}")

            # Perform translation
            translated_text, is_ai_generated = translate_text_if_needed(text, source_language, target_language)

            # Return response
            return JsonResponse({
                "translated_text": translated_text,
                "is_ai_generated": is_ai_generated,
            }, status=200)

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def translate_text(text, target_language):
    url = "http://192.168.1.130:5000/translate"  # Your TensorFlow server endpoint
    payload = {"text": text, "target_language": target_language}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("translated_text", text)
        else:
            print(f"Error from translation server: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TensorFlow server: {e}")
    return text  # Return original text if translation fails


def fetch_and_save_questions():
    flask_url = "http://192.168.1.130:5000/generate-quiz"
    text = "Statistics involves collecting data, testing hypotheses, and analyzing results."
    response = requests.post(flask_url, json={"text": text})
    if response.status_code == 200:
        questions_data = response.json().get("questions", [])
        for question_data in questions_data:
            question, created = Question.objects.get_or_create(text=question_data["question"])
            for idx, option_text in enumerate(question_data["options"]):
                Option.objects.get_or_create(
                    question=question,
                    text=option_text,
                    defaults={"is_correct": idx == question_data["correct_index"]},
                )

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tensorflow_api.models import Question, Option, Translation
import logging
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def quiz_view(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            answers = data.get('answers', {})
            logger.info(f"Parsed answers: {answers}")

            # Processing logic for quiz            
            user_responses = []
            correct_answers = 0
            total_questions = Question.objects.count()

            # Process submitted answers
            for question in Question.objects.prefetch_related('options').all():
                question_id_str = str(question.id)
                submitted_option_id = answers.get(question_id_str)

                if submitted_option_id:  # If the user provided an answer
                    try:
                        selected_option = Option.objects.get(id=submitted_option_id)
                        if selected_option.is_correct:
                            correct_answers += 1  # Increment correct answers count

                        # Log and save response
                        logger.info(f"Saving response: question {question.id}, selected option {selected_option.id}")
                        user_responses.append(
                            Response(
                                question=question,
                                selected_option=selected_option,
                            )
                        )
                    except Option.DoesNotExist:
                        logger.warning(f"Invalid option ID: {submitted_option_id} for question {question.id}")

            # Save user responses
            Response.objects.bulk_create(user_responses)

            # Calculate score
            score = (correct_answers / total_questions) * 100 if total_questions else 0
            badge_path = issue_badge(request.user, score)

            # Return feedback to the user
            return JsonResponse({
                "message": f"Quiz submitted! Your score: {score:.2f}%",
                "score": score,
                "total_questions": total_questions,
            })
        except Exception as e:
            logger.error(f"Error processing quiz submission: {e}")
            return JsonResponse({"error": "Failed to process your submission."}, status=500)

    elif request.method == "GET":
        try:
            # Get the requested language from the query parameters
            requested_language = request.GET.get("lang", "en")
            logger.info(f"Requested language: {requested_language}")

            # Fetch questions
            questions = Question.objects.prefetch_related("options").all()
            translated_questions = []

            for question in questions:
                # Fetch translation from the database
                translation = Translation.objects.filter(
                    original_text=question.text,
                    source_language=question.language,
                    target_language=requested_language
                ).first()

                if translation:
                    translated_question_text = translation.translated_text
                    is_ai_generated = False
                else:
                    # Fallback to translating on the fly if no translation exists
                    translated_question_text, is_ai_generated = translate_text_if_needed(
                        question.text, question.language, requested_language
                    )

                # Translate options
                translated_options = []
                for option in question.options.all():
                    option_translation = Translation.objects.filter(
                        original_text=option.text,
                        source_language=question.language,
                        target_language=requested_language
                    ).first()

                    if option_translation:
                        translated_option_text = option_translation.translated_text
                    else:
                        # Fallback to translating on the fly if no translation exists
                        translated_option_text, _ = translate_text_if_needed(
                            option.text, question.language, requested_language
                        )

                    translated_options.append({
                        "id": option.id,
                        "text": translated_option_text,
                        "image": option.image.url if option.image else None
                    })

                translated_questions.append({
                    "id": question.id,
                    "text": translated_question_text,
                    "options": translated_options,
                    "image": question.image.url if question.image else None,
                    "is_ai_generated": is_ai_generated,
                })

            return JsonResponse({"questions": translated_questions}, safe=False)
        except Exception as e:
            logger.error(f"Error fetching questions: {e}")
            return JsonResponse({"error": "Failed to fetch questions."}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)




@csrf_exempt
def call_tensorflow_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")

            if not text:
                logger.warning("No text provided in the request body.")
                return JsonResponse({"error": "No text provided"}, status=400)

            # Send request to Flask API
            flask_url = "http://192.168.1.130:5000/generate-quiz"
            logger.info(f"Sending request to Flask API at {flask_url} with text: {text}")
            response = requests.post(
                flask_url,
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )

            # Log the raw response
            logger.info(f"Flask response: {response.status_code} - {response.text}")

            # Raise an exception if the status code is an error
            response.raise_for_status()

            # Ensure the response is valid JSON
            return JsonResponse(response.json(), safe=False)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Flask API failed: {e}")
            return JsonResponse({"error": f"Flask API error: {str(e)}"}, status=500)
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            return JsonResponse({"error": "Invalid response from Flask API"}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests allowed."}, status=400)