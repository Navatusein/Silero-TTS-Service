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
        text_number_gender = None

        if len(number) > 1:
            for i in range(1, len(number)):
                word_to_declension = morph.parse(number[i][3:-4])[0]

                if not text_number_gender:
                    text_number_gender = word_to_declension.tag.gender

                inflected_word = word_to_declension.make_agree_with_number(float(number[0]))

                if inflected_word:
                    word_to_declension = inflected_word

                text = text.replace(number[i], word_to_declension.word)

        last_word = morph.parse(text_number.split(' ')[-1])[0]

        if text_number_gender:
            inclined_number = last_word.inflect({text_number_gender})

            if inclined_number:
                text_numbers = text_number.split(' ')
                text_numbers.pop()
                text_numbers.append(inclined_number.word)
                text_number = ' '.join(text_numbers)

        text = text.replace(number[0], text_number)

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
