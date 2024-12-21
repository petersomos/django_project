import requests
import logging

logger = logging.getLogger(__name__)

TRANSLATION_SERVICE_URL = "http://192.168.1.130:5000/translate"  # Adjust the URL as needed

def translate_text_if_needed(text, source_language, target_language):
    try:
        if source_language == target_language:
            logger.debug(f"No translation needed for text: '{text}'")
            return text, False  # No translation needed

        logger.debug(f"Translating from {source_language} to {target_language}: {text}")
        response = requests.post(TRANSLATION_SERVICE_URL, json={
            "text": text,
            "source_language": source_language,
            "target_language": target_language
        })

        response_data = response.json()

        if response.status_code == 200:
            translated_text = response_data.get("translated_text", text)
            is_ai_generated = response_data.get("is_ai_generated", True)
            logger.debug(f"Translation successful: '{translated_text}' (AI: {is_ai_generated})")
            return translated_text, is_ai_generated
        else:
            logger.error(f"Translation failed with error: {response_data.get('error', 'Unknown error')}")
            return text, True
    except Exception as e:
        logger.error(f"Translation service error: {str(e)}")
        return text, True
