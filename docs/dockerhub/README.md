# Silero TTS Service

**Локальный синтез русской и украинской речи для Home Assistant и Rhasspy.**

Offline Russian and Ukrainian text-to-speech based on [Silero](https://github.com/snakers4/silero-models) models with a MaryTTS compatible HTTP API.

Сервис превращает текст в естественную речь и отдаёт WAV по HTTP API, совместимому с MaryTTS. Работает полностью локально, интернет нужен только для скачивания модели при первом запуске.

- 🗣️ 5 русских голосов и украинский голос на моделях Silero `v5_1` и `v4`
- 🔢 Числа и дроби словами, склонение слов после числа
- 🤖 Удаление эмодзи и Markdown: можно озвучивать ответы LLM ассистентов
- 🎛️ SSML, эффекты SoX, кеширование фраз
- 🏠 Работает с интеграцией MaryTTS в Home Assistant и с Rhasspy, есть [аддон Home Assistant](https://github.com/Navatusein/Silero-TTS-Service#install)

🔊 [Послушать примеры голосов и обработки текста](https://github.com/Navatusein/Silero-TTS-Service#features)

## Теги

| Тег | Описание |
|---|---|
| `latest` | Последний релиз |
| `3`, `3.0`, `3.0.1` | Конкретная версия |
| `dev-latest` | Сборка из ветки `dev`, только `amd64` |

Архитектуры: `linux/amd64`, `linux/arm64` (Raspberry Pi 4/5 и другие ARM устройства).

Образ также доступен в GitHub Container Registry: `ghcr.io/navatusein/silero-tts-service`.

## Быстрый старт

```shell
docker run -d -p 9898:9898 -m 1g -e LANGUAGE=ru -v silero-models:/usr/app/models --name silero-tts-service navatusein/silero-tts-service
```

Docker Compose:

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

При первом запуске сервис скачивает модель выбранного языка (до 150 МБ). Том `/usr/app/models` сохраняет её между перезапусками контейнера.

Проверка:

```shell
curl -o speech.wav "http://localhost:9898/process?voice=xenia&text=Привет, мир!"
```

## Переменные окружения

| Переменная | Описание | Значения | По умолчанию |
|---|---|---|---|
| `LANGUAGE` | Язык синтеза речи | `ru`, `uk`, `multi` | `ru` |
| `NUMBER_OF_THREADS` | Количество потоков процессора | от `1` | `4` |
| `SAMPLE_RATE` | Частота дискретизации | `8000`, `24000`, `48000` | `48000` |
| `SOX_PARAM` | Эффекты [SoX](https://linux.die.net/man/1/sox) | например `reverb 50 50 10` | пусто |
| `HA_FIX` | Пауза в конце ответа `POST /process`, чтобы Home Assistant не обрезал фразу | `true`, `false` | `false` |
| `VOICE_TTS_ERRORS` | Озвучивать ошибки вместо ответа `400` | `true`, `false` | `false` |
| `MODELS_DIRECTORY` | Папка для моделей | путь | `./models` |

Голоса:

| Язык | Голоса |
|---|---|
| `ru` | `aidar` `baya` `kseniya` `xenia` `eugene` |
| `uk` | `mykyta` `random` |

## Порт, тома и состояние

| | |
|---|---|
| Порт | `9898` — HTTP API |
| Тома | `/usr/app/models` — скачанные модели, `/usr/app/audios` — кеш синтезированных фраз |
| Healthcheck | Встроенный `HEALTHCHECK` опрашивает `/`. На первое скачивание модели отведено 10 минут |
| Память | Рекомендуется ограничение не меньше `1G` |

## Home Assistant

```yaml
tts:
  - platform: marytts
    host: 192.168.1.10 # Адрес сервера
    port: 9898
    codec: WAVE_FILE
    voice: xenia
```

## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/process?VOICE=xenia&INPUT_TEXT=Привет` | Синтезирует речь и возвращает WAV |
| `POST` | `/process` | То же, параметры `VOICE` и `INPUT_TEXT` в теле (`application/x-www-form-urlencoded`) |
| `GET` | `/voices` | Голоса текущего языка |
| `GET` | `/settings` | Текущие настройки |
| `GET` | `/clear_cache` | Очистка кеша фраз |

Имена параметров не чувствительны к регистру, вместо `INPUT_TEXT` можно передать `text`.

## Ссылки

- [Исходный код и полная документация](https://github.com/Navatusein/Silero-TTS-Service)
- [История изменений](https://github.com/Navatusein/Silero-TTS-Service/blob/main/silero-tts/CHANGELOG.md)
- [Вывод звука на Bluetooth колонку](https://github.com/Navatusein/Silero-TTS-Service/blob/main/docs/bluetooth-speaker/README.md)
- [Сообщить о проблеме](https://github.com/Navatusein/Silero-TTS-Service/issues)

Лицензия: [MIT](https://github.com/Navatusein/Silero-TTS-Service/blob/main/LICENSE)
