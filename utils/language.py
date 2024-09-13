import os
import json

from locales.typing import MultiLanguageTranslations
from django.db.models import Q


def custom_format(template_string, **kwargs):
    import re

    # Pattern to find placeholders in the format {placeholder}
    pattern = r"\{(\w+)\}"

    # Function to replace each match
    def replace(match):
        # Extract the placeholder name from the match
        placeholder = match.group(1)
        # Return the value associated with the placeholder from kwargs if it exists
        # otherwise return the placeholder itself in the same format
        return str(kwargs.get(placeholder, match.group(0)))

    # Use the sub function from re module to replace all matches in the template string
    return re.sub(pattern, replace, template_string)


class TranslationAccessor(MultiLanguageTranslations):
    def __init__(self, multilanguage: "MultiLanguage", path="", language=None):
        self.multilanguage = multilanguage
        self.path = path
        self._lang = language

    def __getattr__(self, key):
        new_path = f"{self.path}.{key}" if self.path else key
        return TranslationAccessor(self.multilanguage, new_path, self._lang)

    def __call__(self, **kwargs):
        # print(self.path, self._lang)
        return self.multilanguage.get(self.path, language=self._lang, **kwargs)

    def __str__(self):
        # Automatically fetch and return the string if no formatting is needed
        result = self.multilanguage.get(self.path, language=self._lang)
        if "{" in result:  # Check if there are placeholders that need formatting
            return f"<callable string: {self.path}>"  # Indicate that this string needs formatting
        return result

    def get_name(self, obj: object) -> str:
        if hasattr(obj, f"name_{self._lang}"):
            return getattr(obj, f"name_{self._lang}")
        return str(obj)

    def filter_name(self, value: str):
        # Create an initial Q object that is False (no conditions)
        query = Q()

        # Combine all conditions using the OR operator
        for lang in self.multilanguage.translations.keys():
            query |= Q(**{f"name_{lang}": value})

        return query

    def get_value(self, obj: object, prefix: str = "name_") -> str:
        if hasattr(obj, f"{prefix}{self._lang}"):
            return getattr(obj, f"{prefix}{self._lang}")
        else:
            print(f"{obj} object has no attribute {prefix}{self._lang}")
        return str(obj)

    str = property(__str__)


class MultiLanguage:
    def __init__(self, folder: str, default_language: str = "uz"):
        self.translations = {}
        self.default_language = default_language
        self.available_languages = set()
        self.load_translations(folder)

    def load_translations(self, folder: str):
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                language_code = filename[:-5]
                self.available_languages.add(language_code)
                file_path = os.path.join(folder, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    # print(file_path)
                    self.translations[language_code] = json.load(file)

    def get_all(self, *text_names, **kwargs):
        all_texts = []

        for language_code, translations in self.translations.items():
            for text_name in text_names:
                translated_text = self.get(text_name, language_code)
                formatted_text = translated_text.format(**kwargs)
                all_texts.append(formatted_text)

        return all_texts

    def get(self, text_name: str, language: str = None, **kwargs):
        language = language or self.default_language
        keys = text_name.split(".")
        language_translations = self.translations.get(language, {})
        nested_translation = language_translations
        for key in keys:
            if key in nested_translation:
                nested_translation = nested_translation[key]
            else:
                return text_name  # Default text if path does not exist
        if isinstance(nested_translation, dict):
            return text_name  # Default text if the final nested object is still a dictionary

        # return nested_translation.format(**kwargs) if kwargs else nested_translation
        return custom_format(nested_translation, **kwargs)

    def __getattr__(self, key):
        # print(key)
        return TranslationAccessor(self, "", key)

    uz: TranslationAccessor
    ru: TranslationAccessor


multilanguage = MultiLanguage("locales")
