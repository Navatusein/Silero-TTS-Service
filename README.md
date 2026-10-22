<div align="center">

# Silero TTS Service

**Локальный синтез русской и украинской речи для Home Assistant и Rhasspy**

[![Release][release-shield]][release-url]
[![Docker Pulls][pulls-shield]][dockerhub-url]
![Supports amd64 Architecture][amd64-shield]
![Supports aarch64 Architecture][aarch64-shield]
[![MIT License][license-shield]][license-url]

</div>

Сервис превращает текст в естественную речь с помощью моделей [Silero] и отдаёт её по HTTP API, совместимому с MaryTTS. Работает полностью локально: никаких облаков, подписок и задержек сети. Интернет нужен только один раз, чтобы скачать модель.

Я сделал этот проект, потому что готовые решения для умного дома говорили по-русски плохо. Вдохновлялся проектом [silero-ha-http-tts] от [Gromina] и довёл идею до готового сервиса с настройками и Docker образами.

https://github.com/user-attachments/assets/a9326a07-9726-41d2-ac45-744fedf3b4ba

> 🔈 GitHub запускает примеры без звука: включите его кнопкой динамика в плеере.

## Содержание

- [Возможности](#features)
- [Установка](#install)
- [Настройки](#settings)
- [Подключение к Home Assistant](#ha-configure)
- [Подключение к Rhasspy](#rhasspy-configure)
- [Обработка текста](#text-processing)
- [API](#api)
- [Вывод звука на Bluetooth колонку](docs/bluetooth-speaker/README.md)
- [Разработка](#development)
- [История изменений](silero-tts/CHANGELOG.md)

<a id="features"></a>
## Возможности

- 🗣️ **Естественные голоса** — 5 русских и украинский голос на моделях Silero `v5_1` и `v4`.
- 🏠 **Аддон Home Assistant** — устанавливается в пару кликов, настройки в интерфейсе HA.
- 🔢 **Числа словами** — целые и дробные, через точку и через запятую: «23.5» → «двадцать три целых пять десятых».
- 📚 **Склонение по числу** — `21 <d>яблоко</d>` → «двадцать одно яблоко», `2 <d>нова</d> <d>книга</d>` → «дві нові книги».
- 🤖 **Готов к ответам LLM** — эмодзи и разметка Markdown удаляются перед синтезом.
- 🎛️ **SSML и эффекты** — паузы, скорость и высота речи, эффекты SoX вроде эха.
- ⚡ **Кеширование** — повторяющиеся фразы озвучиваются мгновенно.
- 🔇 **Озвучивание ошибок** — по желанию колонка скажет «Ошибка синтеза речи» вместо тишины.
- 🧩 **API MaryTTS** — работает со встроенной интеграцией MaryTTS в Home Assistant и с Rhasspy.

<a id="install"></a>
## Установка

### Аддон Home Assistant

[![Добавить репозиторий в Home Assistant][ha-addon-shield]][ha-addon-url]

1. Нажмите кнопку выше или добавьте репозиторий `https://github.com/Navatusein/Silero-TTS-Service` вручную: `Настройки → Дополнения → Магазин дополнений → ⋮ → Репозитории`.
2. Установите аддон **Silero TTS**, выберите язык на вкладке «Конфигурация» и запустите его.
3. [Подключите сервис к Home Assistant](#ha-configure), указав `host: localhost`.

### Docker

```shell
docker run -d -p 9898:9898 -m 1g -e LANGUAGE=ru -v silero-models:/usr/app/models --name silero-tts-service navatusein/silero-tts-service
```

### Docker Compose

Создайте `docker-compose.yml`:

```yaml
services:
  silero-tts-service:
    image: navatusein/silero-tts-service
    container_name: silero-tts-service
    restart: unless-stopped
    ports:
      - "9898:9898"
    volumes:
      - ./models:/usr/app/models
    environment:
      LANGUAGE: ru
      NUMBER_OF_THREADS: 4
    deploy:
      resources:
        limits:
          memory: 1G
```

И запустите:

```shell
docker compose up -d
```

Образы публикуются в [Docker Hub][dockerhub-url] и [GitHub Container Registry][ghcr-url] для `amd64` и `aarch64` (Raspberry Pi 4/5 и другие ARM устройства). Том для моделей нужен, чтобы модель не скачивалась заново при пересоздании контейнера.

<a id="settings"></a>
## Настройки

Настройки передаются переменными окружения контейнера. В аддоне Home Assistant те же настройки задаются на вкладке «Конфигурация» в нижнем регистре.

| Переменная | Описание | Значения | По умолчанию |
|---|---|---|---|
| `LANGUAGE` | Язык синтеза речи | `ru`, `uk`, `multi` | `ru` |
| `NUMBER_OF_THREADS` | Количество потоков процессора для синтеза | от `1` до количества ядер | `4` |
| `SAMPLE_RATE` | Частота дискретизации аудио | `8000`, `24000`, `48000` | `48000` |
| `SOX_PARAM` | Параметры [SoX] для эффектов: эхо, тембр, басы | например `reverb 50 50 10` | пусто |
| `HA_FIX` | Добавляет паузу в конец ответа на `POST /process`, чтобы Home Assistant не обрезал окончание фразы | `true`, `false` | `false` |
| `VOICE_TTS_ERRORS` | При ошибке `/process` возвращает аудио «Ошибка синтеза речи» вместо ответа `400`. Подробности ошибки пишутся в лог | `true`, `false` | `false` |
| `MODELS_DIRECTORY` | Папка для скачанных моделей | путь | `./models` |

Голоса для каждого языка:

| Язык | Код | Голоса |
|:---:|:---:|---|
| Русский | `ru` | `aidar` `baya` `kseniya` `xenia` `eugene` |
| Українська | `uk` | `mykyta` `random` |

<details>
<summary>🔊 Послушать голоса</summary>

**aidar**

https://github.com/user-attachments/assets/faf640d5-8fc3-4959-a30b-39de8c18fe53

**baya**

https://github.com/user-attachments/assets/60acead4-7826-4e90-8d02-2cf7b924f3fd

**kseniya**

https://github.com/user-attachments/assets/0aacce5e-b923-4834-a451-c5a64e2a14ec

**xenia**

https://github.com/user-attachments/assets/a9326a07-9726-41d2-ac45-744fedf3b4ba

**eugene**

https://github.com/user-attachments/assets/0a7ed497-028f-4bc2-b155-10f49f744e9b

**mykyta**

https://github.com/user-attachments/assets/5e2634f6-8625-42a2-bc3f-bd1fb52f82f7

Эти же примеры в формате MP3 лежат в [docs/audio](docs/audio).

</details>

<a id="ha-configure"></a>
## Подключение к Home Assistant

Добавьте в `configuration.yaml`:

```yaml
tts:
  - platform: marytts
    host: localhost # Адрес сервера, для аддона localhost
    port: 9898
    codec: WAVE_FILE
    voice: xenia # Голос из таблицы выше
```

Язык задаётся в настройках сервиса, параметр `language` интеграции MaryTTS не используется.

<a id="rhasspy-configure"></a>
## Подключение к Rhasspy

1. В настройках Rhasspy, в разделе Text to Speech, выберите модуль MaryTTS.
2. Сохраните настройки, Rhasspy перезагрузится.
3. Укажите адрес сервера с путём `/process`, например `http://192.168.1.10:9898/process`.
4. Нажмите Refresh и выберите голос из списка.
5. Сохраните настройки ещё раз.

![Настройки Rhasspy][RhasspyConfig]

<a id="text-processing"></a>
## Обработка текста

Перед синтезом текст проходит нормализацию: так Silero не спотыкается о цифры, латиницу и разметку.

### Числа

Числа читаются словами, дроби можно писать через точку или запятую.

```text
Текст с цифрой 1. На улице 23,5 градуса, а влажность 64.8 процента.
```

https://github.com/user-attachments/assets/c407ff41-87aa-48f5-a4f5-4a0398923fa9

### Склонение слов после числа

Возьмите слово в тег `<d>`, и сервис согласует его с числом. Если склонить нужно несколько слов, каждое берётся в свой тег, а прилагательные согласуются с последним словом по роду.

```text
У меня было 15 <d>яблоко</d>. Мне осталось работать 21 <d>рабочий</d> <d>день</d>.
```

https://github.com/user-attachments/assets/7bb53a15-7259-46e7-966c-bf81c984c7a7

Для украинского языка работает так же, дроби читаются нормативно: «двадцять три цілих п'ять десятих».

```text
На вулиці 23,5 градуса. У мене 21 <d>гривня</d>, 2 <d>нова</d> <d>книга</d> і 5 <d>яблуко</d>.
```

https://github.com/user-attachments/assets/b266412d-47f8-40fc-9ca1-d45cf0db670c

### Латиница

Слова на латинице читаются транслитом.

```text
Lorem ipsum dolor sit amet.
```

https://github.com/user-attachments/assets/712f674d-ee81-4ca4-9a48-89afb8546965

### Эмодзи и Markdown

Эмодзи и разметка Markdown удаляются: заголовки, списки, выделение, ссылки и код. Ответ LLM ассистента можно передавать как есть.

```markdown
# Погода ☀️
- Сегодня **тепло**, плюс 25 <d>градус</d>
- Ветер [слабый](https://example.com) 🌬️
```

Будет озвучено: «Погода. Сегодня тепло, плюс двадцать пять градусов. Ветер слабый.»

https://github.com/user-attachments/assets/72457967-9023-45cf-804d-d5f25b316ae6

### SSML

С помощью SSML можно управлять паузами и просодией речи.

```xml
<p>
  Когда я просыпаюсь, <prosody rate="x-slow">я говорю довольно медленно</prosody>.
  Потом я начинаю говорить своим обычным голосом,
  <prosody pitch="x-high"> а могу говорить тоном выше </prosody>,
  или <prosody pitch="x-low">наоборот, ниже</prosody>.
  Потом, если повезет – <prosody rate="fast">я могу говорить и довольно быстро.</prosody>
  А еще я умею делать паузы любой длины, например две секунды <break time="2000ms"/>.
  <p>
    Также я умею делать паузы между параграфами.
  </p>
  <p>
    <s>И также я умею делать паузы между предложениями</s>
    <s>Вот например как сейчас</s>
  </p>
</p>
```

https://github.com/user-attachments/assets/2a6d7a35-ea32-4ab4-b277-731fec64ebcb

<a id="api"></a>
## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/process?VOICE=xenia&INPUT_TEXT=Привет` | Синтезирует речь и возвращает WAV файл |
| `POST` | `/process` | То же самое, параметры `VOICE` и `INPUT_TEXT` в теле запроса (`application/x-www-form-urlencoded`) |
| `GET` | `/voices` | Список голосов для текущего языка |
| `GET` | `/settings` | Текущие настройки сервера |
| `GET` | `/clear_cache` | Очищает кеш синтезированных фраз |

Имена параметров не чувствительны к регистру, вместо `INPUT_TEXT` можно передать `text`. Если параметр не указан, сервер вернёт `400`.

```shell
curl -o speech.wav "http://localhost:9898/process?voice=xenia&text=Привет, мир!"
```

<a id="development"></a>
## Разработка

Для локального запуска нужны Python 3.14 и [SoX] в `PATH`:

```shell
python -m venv .venv
.venv/bin/pip install -r requirements.txt   # Windows: .venv\Scripts\pip
.venv/bin/python main.py                    # Windows: .venv\Scripts\python
```

Настройки для локального запуска удобно хранить в файле `.env` в корне проекта, имена переменных такие же, как в [таблице настроек](#settings).

Для ручной проверки API есть коллекция Postman: [docs/postman/Silero-TTS-Service.postman_collection.json](docs/postman/Silero-TTS-Service.postman_collection.json). В ней запросы для русского и украинского языка, проверки ответов и примеры обработки текста.

Релиз собирается GitHub Actions при пуше тега версии, например `3.0.0`: образы для `amd64` и `aarch64` публикуются в Docker Hub и GHCR, создаётся черновик релиза. Версия тега должна совпадать с `version` в `app/config.py` и `silero-tts/config.yaml`.

## Благодарности

- [Silero] — за открытые модели синтеза речи.
- [Gromina] — за проект [silero-ha-http-tts], с которого всё началось.

[release-shield]: https://img.shields.io/github/v/release/Navatusein/Silero-TTS-Service?style=for-the-badge
[release-url]: https://github.com/Navatusein/Silero-TTS-Service/releases
[pulls-shield]: https://img.shields.io/docker/pulls/navatusein/silero-tts-service?style=for-the-badge
[dockerhub-url]: https://hub.docker.com/r/navatusein/silero-tts-service
[ghcr-url]: https://github.com/Navatusein/Silero-TTS-Service/pkgs/container/silero-tts-service
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg?style=for-the-badge
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[license-url]: https://github.com/Navatusein/Silero-TTS-Service/blob/main/LICENSE

[ha-addon-shield]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[ha-addon-url]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FNavatusein%2FSilero-TTS-Service

[Silero]: https://github.com/snakers4/silero-models
[silero-ha-http-tts]: https://github.com/Gromina/silero-ha-http-tts
[Gromina]: https://github.com/Gromina
[SoX]: https://linux.die.net/man/1/sox

[RhasspyConfig]: docs/images/RhasspyConfig.png

