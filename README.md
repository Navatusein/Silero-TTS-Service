[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

# Silero TTS Service

## Содержание
- [Установка сервера](#server-install)
- [Настройки сервера](#server-configure)
- [Настройка в Home Assistant](#ha-configure)
- [Настройка в Rhasspy](#rhasspy-configure)


<a id="server-install"></a>
## Установка сервера

### Установка через Docker:
Выполните команду:
```commandline
docker run -p 9898:9898 -e NUMBER_OF_THREADS=4 -e LANGUAGE='ru' -e SAMPLE_RATE=48000 --name tts_silero -d navatusein/silero-tts-service
```

<br/>

### Установка через Docker Compose:
Создайте файл `docker-compose.yml` и перенесите в него содержимое:
```yaml
version: '3'

services:
  silero-tts-service:
    image: "navatusein/silero-tts-service"
    container_name: "silero-tts-service"
    ports:
      - "9898:9898"
    restart: unless-stopped
    environment:
      NUMBER_OF_THREADS: 4
      LANGUAGE: ru
      SAMPLE_RATE: 48000
```
Выполните команду:
```commandline
docker-compose up
```

<br/>

<a id="server-configure"></a>
## Настройки сервера
Все настройки сервера передаются как параметры окружения docker контейнеру при запуске.

Количество ядер для обработки речи `NUMBER_OF_THREADS`:
```yaml
NUMBER_OF_THREADS: 4 
```
Количество потоков от 1 до количества ядер процессора сервера.<br/>
По умолчанию: `4`<br/>
<br/>

Язык синтеза речи `LANGUAGE`:
```yaml
LANGUAGE: 'ru' 
```
По умолчанию: `ru`<br/>

Поддерживаемые языки, с доступными для них голосами:

|    Язык    | Код языка | Поддерживаемые голоса                              |
|:----------:|:---------:|:---------------------------------------------------|
|  Русский   |   `ru`    | `aidar` `baya` `kseniya` `xenia` `eugene` `random` |
| Українська |   `uk`    | `mykyta` `random`                                  |

<br/>

Частота дискретизации `SAMPLE_RATE`:
```yaml
SAMPLE_RATE: 48000 
```
Возможние значения: `48000`, `24000`, `8000`<br/>
По умолчанию: `48000`

<br/>

Параметры утилиты sox `SOX_PARAM`:
```yaml
SOX_PARAM: 'reverb 50 50 10' # Добавляет эхо на речь
```
По умолчанию: Пустой

Выходной файл проходит через утилиту sox. Ей можно передать параметры, чтобы наложить эффекты на речь: поднять тембр, добавить эхо, бас буст включить.

Ссылка на документацию утилиты sox: https://linux.die.net/man/1/sox

<br/>

Исправление обрубания окончания фразы `HA_FIX`:
```yaml
HA_FIX: True 
```
Может принимать значения: `True` `False`<br>
По умолчанию: `False`

Исправляет ошибку, при которой Home Assistant не договаривает конец фразы. Добавляет секунду молчания в конец речи.
 
<br/>

<a id="ha-configure"></a>
### Настройка в Home Assistant
В файле `configuration.yaml` добавьте запись:
```yaml
tts:
  - platform: marytts
    host: localhost # Адрес сервера
    port: 9898
    codec: WAVE_FILE
    voice: xenia # Имя голоса который хотите использовать.
    language: ru # Не используется. Настройки языка указываются в настройках сервера.
```

<br/>

<a id="rhasspy-configure"></a>
### Настройка в Rhasspy Assistant
1) В настройках, в разделе Text to Speech. Выберете модуль MarryTTS.
2) Примените настройки  Rhasspy Assistant (он перезагрузиться).
3) Укажите адрес вашего сервера с путём `/process`.
4) Нажмите на кнопку Refresh.
5) В списке доступных голосов, выберите голос который вам нужно.
6) Примените настройки  Rhasspy Assistant (он перезагрузиться).

![RhasspyConfig]

<br/>


[contributors-shield]: https://img.shields.io/github/contributors/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[contributors-url]: https://github.com/Navatusein/Silero-TTS-Service/graphs/contributors

[stars-shield]: https://img.shields.io/github/stars/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[stars-url]: https://github.com/Navatusein/Silero-TTS-Service/stargazers

[issues-shield]: https://img.shields.io/github/issues/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[issues-url]: https://github.com/Navatusein/Silero-TTS-Service/issues

[license-shield]: https://img.shields.io/github/license/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[license-url]: https://github.com/Navatusein/Silero-TTS-Service/blob/Main/LICENSE

[RhasspyConfig]: /docs/RhasspyConfig.png
[ExampleWithNumber]: /audios/ExampleWithNumber.wav