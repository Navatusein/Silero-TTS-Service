from re import findall, sub
from pymorphy2 import MorphAnalyzer
from transliterate import translit
from num2words import num2words

from app.config import Settings

settings = Settings()

morph = MorphAnalyzer(lang=settings.language)


def normalize_date(text: str) -> str:
    return text


def normalize_time(text: str) -> str:
    return text


def normalize_number(text: str) -> str:
    number_strings = findall(r'(?<![a-zA-Z\d])\d+(?:\.\d+)?(?:(?:\s|\w)*?<d>.*?</d>)*(?!(?:[a-zA-Z\d\"\']|\s)*\'?/?>)',
                             text)

    for number_string in number_strings:
        number_data = number_string.split(' ')

        number = num2words(number_data[0], lang=settings.language)
        number_gender = None

        inflected_words = []

        for i in range(1, len(number_data)):
            if '<d>' not in number_data[i]:
                inflected_words.append(number_data[i])
                continue

            word_to_declension = morph.parse(number_data[i][3:-4])[0]

            if not number_gender:
                number_gender = word_to_declension.tag.gender

            inflected_word = word_to_declension.make_agree_with_number(float(number_data[0]))

            if inflected_word:
                word_to_declension = inflected_word

            inflected_words.append(word_to_declension.word)

        last_number_word = morph.parse(number.split(' ')[-1])[0]

        if number_gender:
            inclined_number = last_number_word.inflect({number_gender})

            if inclined_number:
                numbers = number.split(' ')
                numbers.pop()
                numbers.append(inclined_number.word)
                number = ' '.join(numbers)

        inflected_words.insert(0, number)
        text = text.replace(number_string, ' '.join(inflected_words))

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
