from re import findall, sub
from pymorphy2 import MorphAnalyzer
from transliterate import translit
from num2words import num2words

from app.config import Settings

settings = Settings()

morph = MorphAnalyzer(lang=settings.language)


def normalize_number(text: str) -> str:
    tag_empty_text = sub('<[^>]*[^d]>', '', text)
    numbers = findall(r'\d+(?:\.\d+)?(?:\s<d>.*?</d>)*', tag_empty_text)
    parsed_numbers = [number.split(' ') for number in numbers]

    for number in parsed_numbers:
        text_number = num2words(number[0], lang=settings.language)
        text = text.replace(number[0], text_number)

        if len(number) > 1:
            for i in range(1, len(number)):
                print(number[i])
                word = morph.parse(number[i][3:-4])[0]
                declension_noun = word.make_agree_with_number(float(number[0])).word
                text = text.replace(number[i], declension_noun)

    return text


def translit_text(text: str) -> str:
    tag_empty_text = sub('<[^>]*>', '', text)
    english_words = findall(r'[a-zA-Z]+', tag_empty_text)

    for word in english_words:
        result = translit(word, settings.language)
        text = text.replace(word, result)

    return text


def normalize(text: str) -> str:
    text = " ".join(text.split())
    text = normalize_number(text)
    text = translit_text(text)

    return text
