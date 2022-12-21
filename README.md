![Supports aarch64 Architecture][aarch64-badge]
![Supports amd64 Architecture][amd64-badge]
![Supports armhf Architecture][armhf-badge]
![Supports armv7 Architecture][armv7-badge]
![Supports i386 Architecture][i386-badge]
[![MIT License][license-shield]][license-url]

# Silero TTS Service

## Содержание
- [Установка сервера](#server-install)
- [Настройки сервера](#server-configure)
- [Настройка в Home Assistant](#ha-configure)
- [Настройка в Rhasspy](#rhasspy-configure)
- [Функциональные возможности](#features)

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
## Настройка в Home Assistant
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
## Настройка в Rhasspy Assistant
1) В настройках, в разделе Text to Speech. Выберете модуль MarryTTS.
2) Примените настройки  Rhasspy Assistant (он перезагрузиться).
3) Укажите адрес вашего сервера с путём `/process`.
4) Нажмите на кнопку Refresh.
5) В списке доступных голосов, выберите голос который вам нужно.
6) Примените настройки  Rhasspy Assistant (он перезагрузиться).

![RhasspyConfig]

<br/>

<a id="features"></a>
## Функциональные возможности

### Нормализация цифр
Сервис умеет переводить цифры в текст.<br/>
Пример:
```text
Текст с цифрой 1.
```
[Нормализация Пример 1]

<br/>

### Склонение существительных после цифры
Сервис умеет склонять существительных после цифр.<br/>
Для этого слово которое нужно склонить после цифры, возьмите  в  тег `<d>слово<\d>`.<br/>
Пример:
```text
У меня было 15 <d>яблоко</d>.
```
[Склонение Пример 1]

Если нужно склонить несколько слов, то каждое нужно брать в тег `<d>слово<\d>` отдельно.

```text
Мне осталось работать 15 <d>рабочий</d> <d>день</d>.
```
[Склонение Пример 2]

<br/>

### Произношение транслита
Сервис умеет произносить транслит.<br/>
Пример:
```text
Lorem ipsum dolor sit amet.
```
[Транслит Пример 1]

<br/>

### SSML
С помощью SSML вы можете управлять паузами и просодией синтезированной речи.
```text
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
[SSML Пример 1]

[aarch64-badge]: https://img.shields.io/badge/aarch64-no-red.svg?style=for-the-badge
[amd64-badge]: https://img.shields.io/badge/amd64-yes-green.svg?style=for-the-badge
[armhf-badge]: https://img.shields.io/badge/armhf-no-red.svg?style=for-the-badge
[armv7-badge]: https://img.shields.io/badge/armv7-no-red.svg?style=for-the-badge
[i386-badge]: https://img.shields.io/badge/i386-yes-green.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[license-url]: https://github.com/Navatusein/Silero-TTS-Service/blob/Main/LICENSE

[RhasspyConfig]: /docs/RhasspyConfig.png

[Нормализация Пример 1]: https://on.soundcloud.com/WsG6i

[Склонение Пример 1]: https://on.soundcloud.com/x7RDs
[Склонение Пример 2]: https://on.soundcloud.com/q6Bge

[Транслит Пример 1]: https://on.soundcloud.com/Mfgqv

[SSML Пример 1]: https://on.soundcloud.com/kk9CY