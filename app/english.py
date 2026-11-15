from re import findall, finditer, sub

from app.config import Settings, english_dictionary_file

settings = Settings()

vowel_phonemes = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

# Vowels after a consonant, (after a consonant, at the start of a word or after a vowel)
phoneme_vowels = {
    'ru': {
        'AA': ('а', 'а'), 'AE': ('э', 'э'), 'AH': ('а', 'а'), 'AO': ('о', 'о'), 'AW': ('ау', 'ау'),
        'AY': ('ай', 'ай'), 'EH': ('е', 'э'), 'ER': ('ер', 'эр'), 'EY': ('ей', 'эй'), 'IH': ('и', 'и'),
        'IY': ('и', 'и'), 'OW': ('оу', 'оу'), 'OY': ('ой', 'ой'), 'UH': ('у', 'у'), 'UW': ('у', 'у'),
    },
    'uk': {
        'AA': ('а', 'а'), 'AE': ('е', 'е'), 'AH': ('а', 'а'), 'AO': ('о', 'о'), 'AW': ('ау', 'ау'),
        'AY': ('ай', 'ай'), 'EH': ('е', 'е'), 'ER': ('ер', 'ер'), 'EY': ('ей', 'ей'), 'IH': ('і', 'і'),
        'IY': ('і', 'і'), 'OW': ('оу', 'оу'), 'OY': ('ой', 'ой'), 'UH': ('у', 'у'), 'UW': ('у', 'у'),
    },
}

# Stressed "ER" sounds like "ё" in Russian: "bird" -> "бёрд"
stressed_er = {'ru': ('ёр', 'ёр'), 'uk': ('ер', 'ер')}

# The dictionary reads these vowels as an American would: "on" -> "ан", "Spotify" -> "спотафай".
# They are read as written instead, when the vowel can be matched to a letter
spelled_vowel_phonemes = {'AA', 'AA0', 'AA1', 'AA2', 'AH0'}

spelled_vowels = {
    'ru': {'a': 'а', 'e': 'е', 'i': 'и', 'o': 'о', 'u': 'у', 'y': 'и'},
    'uk': {'a': 'а', 'e': 'е', 'i': 'і', 'o': 'о', 'u': 'у', 'y': 'і'},
}

# "Y" merges with the next vowel: "you" -> "ю"
iotated_vowels = {
    'ru': {'AA': 'я', 'AE': 'я', 'AH': 'я', 'AO': 'ё', 'EH': 'е', 'OW': 'ёу', 'UH': 'ю', 'UW': 'ю'},
    'uk': {'AA': 'я', 'AE': 'я', 'AH': 'я', 'AO': 'йо', 'EH': 'є', 'OW': 'йоу', 'UH': 'ю', 'UW': 'ю'},
}

phoneme_consonants = {
    'ru': {
        'B': 'б', 'CH': 'ч', 'D': 'д', 'DH': 'з', 'F': 'ф', 'G': 'г', 'HH': 'х', 'JH': 'дж', 'K': 'к', 'L': 'л',
        'M': 'м', 'N': 'н', 'NG': 'нг', 'P': 'п', 'R': 'р', 'S': 'с', 'SH': 'ш', 'T': 'т', 'TH': 'с', 'V': 'в',
        'W': 'у', 'Y': 'й', 'Z': 'з', 'ZH': 'ж',
    },
    'uk': {
        'B': 'б', 'CH': 'ч', 'D': 'д', 'DH': 'з', 'F': 'ф', 'G': 'ґ', 'HH': 'г', 'JH': 'дж', 'K': 'к', 'L': 'л',
        'M': 'м', 'N': 'н', 'NG': 'нг', 'P': 'п', 'R': 'р', 'S': 'с', 'SH': 'ш', 'T': 'т', 'TH': 'с', 'V': 'в',
        'W': 'в', 'Y': 'й', 'Z': 'з', 'ZH': 'ж',
    },
}

# Separates a consonant from an iotated vowel: "computer" -> "компьютер", "комп'ютер"
iotation_separators = {
    'ru': {'HH': ''},
    'uk': {'B': "'", 'P': "'", 'V': "'", 'M': "'", 'F': "'", 'R': "'"},
}

# Letter names for abbreviations, "+" marks the stress
letter_names = {
    'ru': {
        'a': '+эй', 'b': 'б+и', 'c': 'с+и', 'd': 'д+и', 'e': '+и', 'f': '+эф', 'g': 'дж+и', 'h': '+эйч', 'i': '+ай',
        'j': 'дж+ей', 'k': 'к+ей', 'l': '+эл', 'm': '+эм', 'n': '+эн', 'o': '+оу', 'p': 'п+и', 'q': 'кь+ю', 'r': '+ар',
        's': '+эс', 't': 'т+и', 'u': '+ю', 'v': 'в+и', 'w': 'дабл+ю', 'x': '+экс', 'y': 'у+ай', 'z': 'з+ед',
    },
    'uk': {
        'a': '+ей', 'b': 'б+і', 'c': 'с+і', 'd': 'д+і', 'e': '+і', 'f': '+еф', 'g': 'дж+і', 'h': '+ейч', 'i': '+ай',
        'j': 'дж+ей', 'k': 'к+ей', 'l': '+ел', 'm': '+ем', 'n': '+ен', 'o': '+оу', 'p': 'п+і', 'q': "к'+ю", 'r': '+ар',
        's': '+ес', 't': 'т+і', 'u': '+ю', 'v': 'в+і', 'w': 'дабл+ю', 'x': '+екс', 'y': 'в+ай', 'z': 'з+ед',
    },
}

# Reading rules for words missing from the dictionary, longer letter combinations go first
letter_rules = {
    'ru': [
        ('sch', 'ш'), ('tch', 'ч'), ('sh', 'ш'), ('ch', 'ч'), ('th', 'т'), ('ph', 'ф'), ('kh', 'х'), ('zh', 'ж'),
        ('ck', 'к'), ('qu', 'кв'), ('oo', 'у'), ('ee', 'и'), ('ea', 'и'), ('ou', 'ау'), ('ai', 'ей'), ('ay', 'ей'),
        ('oy', 'ой'), ('ce', 'се'), ('ci', 'си'), ('cy', 'си'), ('ya', 'я'), ('yu', 'ю'), ('yo', 'ё'), ('ye', 'е'),
        ('a', 'а'), ('b', 'б'), ('c', 'к'), ('d', 'д'), ('e', 'е'), ('f', 'ф'), ('g', 'г'), ('h', 'х'), ('i', 'и'),
        ('j', 'дж'), ('k', 'к'), ('l', 'л'), ('m', 'м'), ('n', 'н'), ('o', 'о'), ('p', 'п'), ('q', 'к'), ('r', 'р'),
        ('s', 'с'), ('t', 'т'), ('u', 'у'), ('v', 'в'), ('w', 'в'), ('x', 'кс'), ('y', 'и'), ('z', 'з'),
    ],
    'uk': [
        ('sch', 'ш'), ('tch', 'ч'), ('sh', 'ш'), ('ch', 'ч'), ('th', 'т'), ('ph', 'ф'), ('kh', 'х'), ('zh', 'ж'),
        ('ck', 'к'), ('qu', 'кв'), ('oo', 'у'), ('ee', 'і'), ('ea', 'і'), ('ou', 'ау'), ('ai', 'ей'), ('ay', 'ей'),
        ('oy', 'ой'), ('ce', 'се'), ('ci', 'сі'), ('cy', 'сі'), ('ya', 'я'), ('yu', 'ю'), ('yo', 'йо'), ('ye', 'є'),
        ('a', 'а'), ('b', 'б'), ('c', 'к'), ('d', 'д'), ('e', 'е'), ('f', 'ф'), ('g', 'ґ'), ('h', 'г'), ('i', 'і'),
        ('j', 'дж'), ('k', 'к'), ('l', 'л'), ('m', 'м'), ('n', 'н'), ('o', 'о'), ('p', 'п'), ('q', 'к'), ('r', 'р'),
        ('s', 'с'), ('t', 'т'), ('u', 'у'), ('v', 'в'), ('w', 'в'), ('x', 'кс'), ('y', 'і'), ('z', 'з'),
    ],
}

# Words the dictionary transcribes in a way that sounds unnatural in Russian or Ukrainian
word_overrides = {
    'ru': {'the': 'зэ', 'a': 'э'},
    'uk': {'the': 'зе', 'a': 'е'},
}


def load_dictionary() -> dict[str, list[str]]:
    dictionary = {}

    with open(english_dictionary_file, encoding='utf-8') as file:
        for line in file:
            word, _, phonemes = line.partition('#')[0].strip().partition(' ')

            # Alternative pronunciations are marked as "word(2)", the first one is the most common
            if word and '(' not in word:
                dictionary[word] = phonemes.split()

    return dictionary


dictionary = load_dictionary() if settings.language in phoneme_vowels else {}


def remove_silent_e(word: str) -> str:
    # Final "e" after a consonant is silent: "home", "smartphone"
    return sub(r'(?<=[^aeiouy])e$', '', word) if len(word) > 3 else word


def get_vowel_letters(word: str) -> list[str]:
    # "Y" before a vowel is a consonant: "you", "player"
    return [match.group(0) for match in finditer(r'[aeiou]+|y(?![aeiou])', remove_silent_e(word))]


def phonemes_to_cyrillic(phonemes: list[str], word: str) -> str:
    language = settings.language
    vowel_letters = get_vowel_letters(word)
    # Vowel sounds can be matched to letters only when the word has as many vowel letter groups
    aligned = len(vowel_letters) == sum(phoneme.rstrip('012') in vowel_phonemes for phoneme in phonemes)
    vowel_index = -1
    result = ''
    stressed = False
    previous = None
    i = 0

    while i < len(phonemes):
        phoneme = phonemes[i].rstrip('012')
        stress = phonemes[i][len(phoneme):]
        after_vowel = previous is None or previous in vowel_phonemes

        if phoneme == 'Y' and i + 1 < len(phonemes) and phonemes[i + 1].rstrip('012') in iotated_vowels[language]:
            phoneme = phonemes[i + 1].rstrip('012')
            stress = phonemes[i + 1][len(phoneme):]
            letters = iotated_vowels[language][phoneme]

            if not after_vowel:
                letters = iotation_separators[language].get(previous, 'ь' if language == 'ru' else '') + letters

            vowel_index += 1
            i += 1
        elif phoneme in vowel_phonemes:
            vowel_index += 1

            # Unstressed vowel before a final "L" is not pronounced: "google" -> "гугл", "apple" -> "эпл"
            if phoneme == 'AH' and stress == '0' and not after_vowel and phonemes[i + 1:] == ['L']:
                previous = phoneme
                i += 1
                continue

            forms = stressed_er[language] if phoneme == 'ER' and stress == '1' else phoneme_vowels[language][phoneme]
            letters = forms[1] if after_vowel else forms[0]
            vowel_letter = vowel_letters[vowel_index] if aligned else ''

            if phonemes[i] in spelled_vowel_phonemes and vowel_letter in spelled_vowels[language]:
                letters = spelled_vowels[language][vowel_letter]

                # "э" keeps the sound hard at the start of a word and after a vowel
                if letters == 'е' and after_vowel and language == 'ru':
                    letters = 'э'
        else:
            letters = phoneme_consonants[language].get(phoneme, '')

        # Only the first primary stress is marked, Silero expects one stress per word
        if phoneme in vowel_phonemes and stress == '1' and not stressed:
            stress_index = next(j for j, letter in enumerate(letters) if letter in 'аеёиоуэюяєії')
            letters = letters[:stress_index] + '+' + letters[stress_index:]
            stressed = True

        result += letters
        previous = phoneme
        i += 1

    return result


def spell_abbreviation(word: str) -> str:
    names = [letter_names[settings.language][letter] for letter in word.lower()]

    # The stress falls on the last letter: "USB" -> "юэсб+и"
    return ''.join(name.replace('+', '') for name in names[:-1]) + names[-1]


def read_by_rules(word: str) -> str:
    word = remove_silent_e(word.lower())
    result = ''

    while word:
        letters, replacement = next((rule for rule in letter_rules[settings.language] if word.startswith(rule[0])),
                                    (word[0], ''))
        result += replacement
        word = word[len(letters):]

    return result


def find_in_dictionary(word: str) -> str | None:
    lower_word = word.lower()

    if lower_word in word_overrides[settings.language]:
        return word_overrides[settings.language][lower_word]

    if lower_word in dictionary:
        return phonemes_to_cyrillic(dictionary[lower_word], lower_word)

    return None


def english_word_to_cyrillic(word: str) -> str:
    # Short uppercase words and words without vowels are abbreviations: "USB", "HDMI", "TV"
    if len(word) > 1 and word.isupper() and (len(word) <= 4 or not findall(r'[AEIOUY]', word)):
        return spell_abbreviation(word)

    result = find_in_dictionary(word)

    if result is not None:
        return result

    # Hyphenated and camel case words are read by parts: "Wi-Fi", "HomeAssistant"
    parts = [part for part in sub(r'([a-z])([A-Z])', r'\1 \2', word.replace('-', ' ')).split(' ') if part]

    if len(parts) > 1:
        return ' '.join(english_word_to_cyrillic(part) for part in parts)

    # Compound words missing from the dictionary: "smarthome" -> "smart" + "home", stressed on the first part
    for i in range(len(word) - 3, 2, -1):
        left, right = find_in_dictionary(word[:i]), find_in_dictionary(word[i:])

        if left is not None and right is not None:
            return left + right.replace('+', '')

    return read_by_rules(word)


def english_to_cyrillic(text: str) -> str:
    # There is no phoneme mapping for the multi language model, it reads Latin letters by itself
    if settings.language not in phoneme_vowels:
        return text

    # Tags are matched first and kept as is, so SSML tag and attribute names stay in English
    return sub(r"<[^>]*>|[a-zA-Z]+(?:['’-][a-zA-Z]+)*",
               lambda match: match.group(0) if match.group(0).startswith('<')
               else english_word_to_cyrillic(match.group(0).replace('’', "'")), text)
