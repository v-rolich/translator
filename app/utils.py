import os
import requests

from app.schemas import WordInfo


def fetch_and_parse_google_translate(word: str, target_language: str, source_language: str) -> WordInfo:
    """
    Translate and parse a word.
    """
    translations = translate_text(word, target_language, source_language)
    definitions, synonyms, examples = get_definitions_synonyms_examples(word, target_language, source_language)
    return WordInfo(
        word=word,
        translations=translations,
        definitions=definitions,
        synonyms=synonyms,
        examples=examples,
    )


def translate_text(word: str, target_language: str, source_language: str = 'auto') -> list[str]:
    """
    Translate word using the Google Cloud Translation API.
    """
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": os.getenv("CLOUD_API_KEY"),
        "q": word,
        "source": source_language,
        "target": target_language,
        "format": "text",
    }
    response = requests.post(url, params=params)

    if response.status_code == 200:
        translated_data = response.json().get('data', {}).get('translations', [])
        return [translation.get("translatedText") for translation in translated_data]
    else:
        response.raise_for_status()


def get_definitions_synonyms_examples(word: str, target_language: str, source_language: str = 'auto') -> tuple:
    """
    This is a hypothetical function to get lists with word definitions, synonyms and examples.
    """
    return None, None, None


def parse_words_extraction(
        words: list[dict], include_definitions: bool, include_synonyms: bool, include_examples: bool) -> list[dict]:
    """
    Parse list of words based on parameters
    """
    word_list = []
    for word in words:
        word_dict = {"word": word["word"]}
        if include_definitions:
            word_dict["definitions"] = word["definitions"]
        if include_synonyms:
            word_dict["synonyms"] = word["synonyms"]
        if include_examples:
            word_dict["examples"] = word["examples"]
        word_list.append(word_dict)

    return word_list
