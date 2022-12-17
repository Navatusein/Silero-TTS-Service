from re import findall
from pymorphy2 import MorphAnalyzer
from transliterate import translit
from num2words import num2words

from app.config import Settings

settings = Settings()

morph = MorphAnalyzer(lang=settings.language)


def normalize_number(text: str) -> str:
    numbers = findall(r'\d+(?:\.\d+)?(?:\s<d>.*?</d>)*', text)
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
    result = translit(text, settings.language)
    return result


def normalize(text: str) -> str:
    text = " ".join(text.split())
    text = normalize_number(text)
    text = translit_text(text)

    return text
