from re import DOTALL, IGNORECASE, MULTILINE, Match, search, sub
from emoji import replace_emoji
from pymorphy3 import MorphAnalyzer
from pymorphy3.analyzer import Parse
from num2words import num2words

from app.config import Settings
from app.english import english_to_cyrillic

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


months = {
    'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
           'ноября', 'декабря'],
    'uk': ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня',
           'листопада', 'грудня'],
}

# Year words after a year number and their cases, None for an abbreviation or an ambiguous form
year_words = {
    'ru': {'год': 'nomn', 'года': 'gent', 'году': None, 'годом': 'ablt', 'годе': 'loct', 'г': None},
    'uk': {'рік': 'nomn', 'року': 'gent', 'році': 'loct', 'роком': 'ablt', 'р': None},
}

# Year word in the genitive and the locative case, an abbreviation is replaced with one of them
year_word_forms = {'ru': ('года', 'году'), 'uk': ('року', 'році')}

# The case of a date or a time depends on the word before it: "до 15 ноября" -> "до пятнадцатого ноября"
case_words = {
    'ru': {
        'gent': ['до', 'с', 'со', 'от', 'после', 'около', 'для', 'без', 'кроме'],
        'datv': ['к', 'ко'],
        'loct': ['в', 'во'],
        'accs': ['на', 'за', 'про', 'через', 'по'],
        'nomn': ['сегодня', 'завтра', 'вчера', 'послезавтра', 'позавчера', 'дата', 'понедельник', 'вторник', 'среда',
                 'четверг', 'пятница', 'суббота', 'воскресенье'],
    },
    'uk': {
        'gent': ['до', 'з', 'із', 'зі', 'від', 'після', 'біля', 'близько', 'для', 'без', 'крім'],
        'loct': ['о', 'об', 'в', 'у'],
        'accs': ['на', 'за', 'про', 'через'],
        'nomn': ['сьогодні', 'завтра', 'вчора', 'учора', 'післязавтра', 'позавчора', 'дата', 'понеділок', 'вівторок',
                 'середа', 'четвер', "п'ятниця", 'субота', 'неділя'],
    },
}


# The Ukrainian dictionary has no singular forms of "година"
uk_hour_forms = {'nomn': 'година', 'gent': 'години', 'datv': 'годині', 'accs': 'годину', 'loct': 'годині'}


def get_case(match: Match, default: str) -> str:
    previous_word = search(r"([^\W\d_][\w']*)[\s,:—–-]*$", match.string[:match.start()])

    if not previous_word:
        return default

    word = previous_word.group(1).lower()

    return next((case for case, words in case_words.get(settings.language, {}).items() if word in words), default)


def inflect_number_word(word: str, grammemes: set[str]) -> str:
    parses = morph.parse(word)
    parse = next((parse for parse in parses if parse.tag.POS == 'NUMR' or 'Anum' in parse.tag), parses[0])
    inflected = parse.inflect(grammemes)

    return inflected.word if inflected else word


def number_with_noun(number: int, noun_word: str, case: str) -> str:
    noun = morph.parse(noun_word)[0]
    numbers = num2words(number, lang=settings.language).split(' ')
    numbers[-1] = number_gender_forms.get(settings.language, {}).get(numbers[-1], {}).get(noun.tag.gender, numbers[-1])

    if case in ('nomn', 'accs', 'loct'):
        noun = agree_with_number(noun, str(number), noun.tag.gender)
    else:
        # In other cases both the number and the noun take the case: "до двадцати одного часа", "к двум часам"
        numbers = [inflect_number_word(word, {case}) for word in numbers]
        noun = noun.inflect({case, 'sing' if number % 10 == 1 and number % 100 != 11 else 'plur'}) or noun

    return ' '.join(numbers + [noun.word])


def ordinal_to_words(number: int, grammemes: set[str]) -> str:
    words = num2words(number, lang=settings.language, to='ordinal').split(' ')

    # Only the last word of an ordinal number is inflected: "две тысячи двадцать шестого"
    parses = morph.parse(words[-1])
    parse = next((parse for parse in parses if parse.tag.POS == 'ADJF' and {'masc', 'nomn'} in parse.tag), None)
    inflected = parse.inflect(grammemes) if parse else None
    words[-1] = inflected.word if inflected else words[-1]

    return ' '.join(words)


def date_to_words(match: Match, day: str, month: str, year: str | None, month_word: str | None = None) -> str:
    if not 1 <= int(day) <= 31 or not 1 <= int(month) <= 12:
        return match.group(0)

    # Without a preposition the date is read in the genitive case: "встреча пятнадцатого ноября"
    case = get_case(match, 'gent')
    case = 'nomn' if case in ('accs', 'loct') else case
    words = [ordinal_to_words(int(day), {'neut', case}), month_word or months[settings.language][int(month) - 1]]

    if year:
        words += [ordinal_to_words(int(year), {'masc', 'gent'}), year_word_forms[settings.language][0]]

    return ' '.join(words)


def normalize_date(text: str) -> str:
    if settings.language not in months:
        return text

    # The dot after an abbreviation is dropped when the sentence goes on: "в 2024 г. было" -> "в 2024 году было"
    year_word_pattern = rf'(?:{"|".join(year_words[settings.language])})\b(?:(?<=[гр])\.(?=\s+[a-zа-яёієїґ]))?'

    # ISO date, a time after "T" is read separately: "2026-11-15T14:30"
    text = sub(r'(?<![\d.,:/-])(\d{4})-(\d{1,2})-(\d{1,2})(?:(T)(?=\d)|(?![\d-]))',
               lambda match: date_to_words(match, match.group(3), match.group(2), match.group(1))
               + (' ' if match.group(4) else ''), text)

    # Numeric date with a year: "15.11.2026", "15/11/2026", "15.11.2026 г."
    text = sub(rf'(?<![\d.,:/])(\d{{1,2}})([./])(\d{{1,2}})\2(\d{{4}})(?:\s*{year_word_pattern})?(?![\d.,/]*\d)',
               lambda match: date_to_words(match, match.group(1), match.group(3), match.group(4)), text)

    # Date with a month name: "15 ноября", "15 ноября 2026 года"
    month_pattern = '|'.join(months[settings.language])
    text = sub(rf'(?<![\d.,])(\d{{1,2}})\s+({month_pattern})\b(?:\s+(\d{{4}})(?:\s*{year_word_pattern})?)?',
               lambda match: date_to_words(match, match.group(1),
                                           str(months[settings.language].index(match.group(2).lower()) + 1),
                                           match.group(3), match.group(2)), text, flags=IGNORECASE)

    # Year with a year word: "в 2026 году", "2026 рік"
    return sub(rf'(?<![\d.,])([12]\d{{3}})\s+({year_word_pattern})', year_match_to_words, text, flags=IGNORECASE)


def year_match_to_words(match: Match) -> str:
    year_word = match.group(2).lower().rstrip('.')
    case = year_words[settings.language][year_word]

    if case is None:
        # "году" is the locative case after "в" and the dative case otherwise: "в 2026 году", "к 2026 году".
        # An abbreviation is read in the locative case after "в" and in the genitive case otherwise
        locative = get_case(match, 'gent') == 'loct'
        case = 'loct' if locative else 'datv' if year_word == 'году' else 'gent'

        if year_word not in year_word_forms[settings.language]:
            year_word = year_word_forms[settings.language][locative]

    return f'{ordinal_to_words(int(match.group(1)), {"masc", case})} {year_word}'


def time_to_words(match: Match) -> str:
    hours, minutes, seconds = int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)
    case = get_case(match, 'nomn')

    if settings.language == 'uk' and hours:
        # Ukrainian hours are ordinal: "о чотирнадцятій годині", "чотирнадцята година"
        words = [ordinal_to_words(hours, {'femn', case}), uk_hour_forms.get(case, 'година')]
        minutes_case = 'gent' if case == 'gent' else 'nomn'
    else:
        words = [number_with_noun(hours, 'час' if settings.language == 'ru' else 'година', case)]
        minutes_case = case

    if minutes or seconds:
        words.append(number_with_noun(minutes, 'минута' if settings.language == 'ru' else 'хвилина', minutes_case))

    if seconds:
        words.append(number_with_noun(seconds, 'секунда', minutes_case))

    return ' '.join(words)


def normalize_time(text: str) -> str:
    if settings.language not in months:
        return text

    # Minutes are always two digits, so ratios and scores like "16:9" or "2:1" stay numbers
    return sub(r'(?<![\d.,:+])([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d)(?:[.,]\d+)?)?(?![\d:])', time_to_words, text)


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


def remove_markdown(text: str) -> str:
    for pattern, replacement, flags in markdown_patterns:
        text = sub(pattern, replacement, text, flags=flags)

    return text


def normalize(text: str) -> str:
    text = replace_emoji(text, replace='')
    text = remove_markdown(text)
    text = " ".join(text.split())
    text = normalize_date(text)
    text = normalize_time(text)
    text = normalize_number(text)
    text = english_to_cyrillic(text)

    return text
