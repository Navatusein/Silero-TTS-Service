![Supports aarch64 Architecture][aarch64-badge]
![Supports amd64 Architecture][amd64-badge]
![Supports armhf Architecture][armhf-badge]
![Supports armv7 Architecture][armv7-badge]
![Supports i386 Architecture][i386-badge]
[![MIT License][license-shield]][license-url]

# Silero TTS Service

## Содержание
- [Информация](#information)
- [Установка сервера](#server-install)
- [Настройки сервера](#server-configure)
- [Настройка в Home Assistant](#ha-configure)
- [Настройка в Rhasspy](#rhasspy-configure)
- [Функциональные возможности](#features)
- [Endpoints](#endpoints)
- [Вывод звука на Bluetooth колонку](#bluetooth-speaker)


<a id="information"></a>
## Информация
 Данный проект я создал, чтобы обеспечить свой умный дом нормальным синтезом речи. Также, чтобы обеспечить  rhasspy нормальным синтезом речи. Уже готовые решения меня не устроили и было решено изобрести свой велосипед. За основу были взяты модели [Silero].

Вдохновился я проектом [silero-ha-http-tts] от [Gromina]. Он был сыроват и я решил сделать всё по уму разуму, с настройками и готовыми контейнерами.  
<br/>

<a id="server-install"></a>
## Установка сервера

### Установка через Docker:
Выполните команду:
```commandline
docker run -p 9898:9898 -m 1g -e NUMBER_OF_THREADS=4 -e LANGUAGE=ru -e SAMPLE_RATE=48000 --name tts_silero -d navatusein/silero-tts-service
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
    deploy:
      resources:
        limits:
          memory: 1G
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
LANGUAGE: ru
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
SOX_PARAM: "reverb 50 50 10" # Добавляет эхо на речь
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
Для этого слово которое нужно склонить после цифры, возьмите  в  тег `<d>слово</d>`.<br/>
Пример:
```text
У меня было 15 <d>яблоко</d>.
```
[Склонение Пример 1]

Если нужно склонить несколько слов, то каждое нужно брать в тег `<d>слово</d>` отдельно.

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

<br/>

<a id="endpoints"></a>
## Endpoints
- `GET` `/clear_cache` - Очищает кэш уже синтезированных сообщений.
- `GET` `/settings` - Возвращает текущие настройки сервера.
- `GET` `/voices` - Возвращает список доступных голосов для выбранного языка.
- `GET` `/process?VOICE=[Выбраный голос]&INPUT_TEXT=[Текст для обработки]` - Возвращает аудио файл синтезированной речи.
- `POST` `/process` в теле запроса `VOICE=[Выбраный голос]`, `INPUT_TEXT=[Текст для обработки]` - Возвращает аудио файл синтезированной речи.

<br/>

<a id="bluetooth-speaker"></a>
## Вывод звука на Bluetooth колонку

1) Если Home Assistant как основная ОС (HAOS), то читаем эту документацию [TTS Bluetooth Speaker for Home Assistant]
2) Если Home Assistant стоит на Debian, то делаем следующее:

Отредактируем client.conf

```commandline
nano /etc/pulse/client.conf
```

Добавим следующее:

```commandline
default-server = unix:/usr/share/hassio/audio/external/pulse.sock
autospawn = no
```

![ClientConf]

Перезапускаем pulseaudio.

```commandline
pulseaudio -k && pulseaudio --start
```

Ставим аддон [Mopidy версии Current version: 2.1.1] и ставим только эту версию. Mopidy 2.2.0 не ставить - она сломанная. Подробнее про поломанную версию Mopidy 2.2.0 читать [здесь].

Добавляем в configuration.yaml
```yaml
media_player:
  - platform: mpd
    name: "MPD Mopidy"
    host: localhost
    port: 6600
```

Перезагружаем Home Assistant полностью, чтобы перезагрузился сам Debian.

![RebootHa]

Подключаем bluetooth колонку к Debian, kb,j через GUI, либо через консоль используя команду bluetoothctl

Включим bluetooth:

```commandline
power on
```

Запуск сканирования девайсов:

```commandline
scan on
```

Как увидели свой девайс, спариваемся с устройством:

```commandline
pair [mac адрес девайса]
```

Подключаемся к устройству:

```commandline
connect [mac адрес девайса]
```

Добавляем устройство в доверенные:

```commandline
trust [mac адрес девайса]
```

Далее, как добавлен bluetooth девайс то в двух аддонов Rhasspy Assistant и Mopidy нужно указать источник вывода звука bluetooth девайса:

1) В Rhasspy Assistant указываем так:

![RhasspyAssistantConfig]

2) В Mopidy указываем так:

![MopidyConfig]


Проверяем работоспособность:

![TtsSay]

Код: 

```yaml
service: tts.marytts_say
data:
  entity_id: media_player.mpd_mopidy
  message: >-
    Спустя 15 лет жизнь некогда бороздившего космические просторы Жана-Люка
    Пикара
```

[aarch64-badge]: https://img.shields.io/badge/aarch64-no-red.svg?style=for-the-badge
[amd64-badge]: https://img.shields.io/badge/amd64-yes-green.svg?style=for-the-badge
[armhf-badge]: https://img.shields.io/badge/armhf-no-red.svg?style=for-the-badge
[armv7-badge]: https://img.shields.io/badge/armv7-no-red.svg?style=for-the-badge
[i386-badge]: https://img.shields.io/badge/i386-yes-green.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/Navatusein/Silero-TTS-Service.svg?style=for-the-badge
[license-url]: https://github.com/Navatusein/Silero-TTS-Service/blob/Main/LICENSE

[Silero]: https://github.com/snakers4/silero-models

[silero-ha-http-tts]: https://github.com/Gromina/silero-ha-http-tts
[Gromina]: https://github.com/Gromina

[RhasspyConfig]: /docs/RhasspyConfig.png

[Нормализация Пример 1]: https://on.soundcloud.com/WsG6i

[Склонение Пример 1]: https://on.soundcloud.com/x7RDs
[Склонение Пример 2]: https://on.soundcloud.com/q6Bge

[Транслит Пример 1]: https://on.soundcloud.com/Mfgqv

[SSML Пример 1]: https://on.soundcloud.com/kk9CY

[TTS Bluetooth Speaker for Home Assistant]: https://github.com/pkozul/ha-tts-bluetooth-speaker

[ClientConf]: /docs/ClientConf.png

[Mopidy версии Current version: 2.1.1]: https://github.com/Llntrvr/Hassio-Addons

[здесь]: https://github.com/Poeschl/Hassio-Addons/issues/334

[RebootHa]: /docs/RebootHa.png

[RhasspyAssistantConfig]: /docs/RhasspyAssistantConfig.png
[MopidyConfig]: /docs/MopidyConfig.png
[TtsSay]: /docs/TtsSay.png