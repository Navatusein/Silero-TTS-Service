from re import DOTALL, MULTILINE, Match, findall, sub
from emoji import replace_emoji
from pymorphy3 import MorphAnalyzer
from pymorphy3.analyzer import Parse
from transliterate import translit
from num2words import num2words

from app.config import Settings

settings = Settings()

morph = MorphAnalyzer(lang=settings.language)

number_gender_forms = {
    'ru': {'один': {'femn': 'одна', 'neut': 'одно'}, 'два': {'femn': 'две'}},
    'uk': {'один': {'femn': 'одна', 'neut': 'одне'}, 'два': {'femn': 'дві'}},
}


def end_sentence(match: Match) -> str:
    line = match.group(1)

    # Headers and list items have no ending punctuation, add it to pause between lines
    return line if line[-1] in '.,:;!?…' else f'{line}.'


markdown_patterns = [
    (r'```[^\n]*\n?(.*?)```', r'\1', DOTALL),  # code block, keep the content
    (r'^[ \t]*(?:[-*_][ \t]*){3,}$', '', MULTILINE),  # horizontal rule
    (r'^[ \t]{0,3}#{1,6}[ \t]+(.+?)[ \t]*$', end_sentence, MULTILINE),  # header
    (r'^[ \t]*>[ \t]?', '', MULTILINE),  # quote
    (r'^[ \t]*[-*+][ \t]+(.+?)[ \t]*$', end_sentence, MULTILINE),  # bullet list item
    (r'^([ \t]*\d+\.[ \t]+.+?)[ \t]*$', end_sentence, MULTILINE),  # numbered list item
    (r'!\[([^\]]*)\]\([^)]*\)', r'\1', 0),  # image, keep the alt text
    (r'\[([^\]]+)\]\([^)]*\)', r'\1', 0),  # link, keep the text
    (r'(\*\*|__)(?!\s)(.+?)(?<!\s)\1', r'\2', 0),  # bold
    (r'(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])', r'\1', 0),  # italic
    (r'(?<!\w)_(?![\s_])(.+?)(?<![\s_])_(?!\w)', r'\1', 0),  # italic
    (r'~~(.+?)~~', r'\1', 0),  # strikethrough
    (r'`([^`]*)`', r'\1', 0),  # inline code
]

uk_fraction_denominators = [
    ('десята', 'десятих'),
    ('сота', 'сотих'),
    ('тисячна', 'тисячних'),
    ('десятитисячна', 'десятитисячних'),
    ('стотисячна', 'стотисячних'),
    ('мільйонна', 'мільйонних'),
]


def normalize_date(text: str) -> str:
    return text


def normalize_time(text: str) -> str:
    return text


def normalize_number(text: str) -> str:
    # Three or more numbers joined by commas are a list, not a decimal: "1,2,3" -> "1, 2, 3"
    text = sub(r'(?<![\d.,])\d+(?:,\d+){2,}(?![\d.,]*\d)', lambda match: ', '.join(match.group(0).split(',')), text)

    return sub(r'(?<![a-zA-Z\d])\d+(?:[.,]\d+)?(?:(?:\s|[^\W\d])*?<d>.*?</d>)*(?!(?:[a-zA-Z\d\"\']|\s)*\'?/?>)',
               normalize_number_match, text)


def normalize_number_match(match: Match) -> str:
    number_data = match.group(0).split(' ')
    number_value = number_data[0].replace(',', '.')

    number = number_to_words(number_value)
    number_gender = None

    inflected_words = number_data[1:]
    declension_indexes = [i for i, word in enumerate(inflected_words) if '<d>' in word]

    if declension_indexes:
        # The last word to declension is the noun, words before it are adjectives
        noun = morph.parse(inflected_words[declension_indexes[-1]][3:-4])[0]
        number_gender = noun.tag.gender

        for i in declension_indexes:
            if i == declension_indexes[-1]:
                word_to_declension = noun
            else:
                parses = morph.parse(inflected_words[i][3:-4])
                word_to_declension = next((parse for parse in parses if parse.tag.POS == 'ADJF'), parses[0])

            inflected_words[i] = agree_with_number(word_to_declension, number_value, number_gender).word

    if number_gender and '.' not in number_value:
        numbers = number.split(' ')
        numbers[-1] = number_gender_forms.get(settings.language, {}).get(numbers[-1], {}).get(number_gender, numbers[-1])
        number = ' '.join(numbers)

    inflected_words.insert(0, number)

    return ' '.join(inflected_words)


def number_to_words(number_value: str) -> str:
    whole, _, fraction = number_value.partition('.')

    # num2words reads uk decimals as "три кома п'ять", build "три цілих п'ять десятих" instead
    if settings.language != 'uk' or not fraction or len(fraction) > len(uk_fraction_denominators):
        return num2words(number_value, lang=settings.language)

    def with_form(value: str, forms: tuple[str, str]) -> str:
        number = int(value)
        form = forms[0] if number % 10 == 1 and number % 100 != 11 else forms[1]
        return f'{num2words(number, lang="uk", gender="feminine")} {form}'

    return f'{with_form(whole, ("ціла", "цілих"))} {with_form(fraction, uk_fraction_denominators[len(fraction) - 1])}'


def agree_with_number(word: Parse, number_value: str, gender: str | None) -> Parse:
    if '.' in number_value:
        return word.inflect({'gent'}) or word

    number = int(number_value)

    if number % 10 == 1 and number % 100 != 11:
        if word.tag.POS == 'ADJF' and gender:
            return word.inflect({gender}) or word

        return word

    if settings.language != 'uk':
        return word.make_agree_with_number(number) or word

    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return word.inflect({'plur', 'nomn'}) or word

    return word.inflect({'plur', 'gent'}) or word


def translit_text(text: str) -> str:
    tag_empty_text = sub('<[^>]*>', '', text)
    english_words = findall(r'[a-zA-Z]+', tag_empty_text)

    for word in english_words:
        result = translit(word, settings.language)
        text = text.replace(word, result)

    return text


def remove_markdown(text: str) -> str:
    for pattern, replacement, flags in markdown_patterns:
        text = sub(pattern, replacement, text, flags=flags)

    return text


def normalize(text: str) -> str:
    text = replace_emoji(text, replace='')
    text = remove_markdown(text)
    text = " ".join(text.split())
    text = normalize_number(text)
    text = translit_text(text)

    return text
