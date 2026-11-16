import wave
import logging
from functools import partial

from wyoming.audio import wav_to_chunks
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

from app.config import Settings, version
from app.normalizer import normalize
from app.tts import get_audio_file

logger = logging.getLogger('uvicorn')

samples_per_chunk = 1024
attribution = Attribution(name='Navatusein/Silero-TTS-Service',
                          url='https://github.com/Navatusein/Silero-TTS-Service')


def build_info(settings: Settings) -> Info:
    speakers = settings.silero_settings[settings.language]['speakers']

    voices = [
        TtsVoice(name=speaker, attribution=attribution, installed=True,
                description=f'Silero {settings.language} voice: {speaker}',
                version=None, languages=[settings.language])
        for speaker in speakers
    ]

    program = TtsProgram(name='silero-tts-service', attribution=attribution, installed=True,
                         description='Silero TTS Service', version=version,
                         voices=voices, supports_synthesize_streaming=False)

    return Info(tts=[program])


class WyomingTtsHandler(AsyncEventHandler):
    def __init__(self, settings: Settings, wyoming_info: Info, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.wyoming_info = wyoming_info

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info.event())
            return True

        if Synthesize.is_type(event.type):
            await self._handle_synthesize(Synthesize.from_event(event))
            return True

        return True

    async def _handle_synthesize(self, synthesize: Synthesize) -> None:
        speakers = self.settings.silero_settings[self.settings.language]['speakers']
        requested = synthesize.voice.name if synthesize.voice else None
        speaker = requested if requested in speakers else speakers[0]

        text = normalize(synthesize.text)
        text = f'<speak>{text}</speak>'

        try:
            audio_file = get_audio_file(text=text, speaker=speaker)
        except RuntimeError as exception:
            logger.error(f'Wyoming synthesis failed: {exception}')
            await self.write_event(Error(text=str(exception), code='synthesize_failed').event())
            return

        with wave.open(audio_file, 'rb') as wav_file:
            for wyoming_event in wav_to_chunks(wav_file, samples_per_chunk,
                                               start_event=True, stop_event=True):
                await self.write_event(wyoming_event.event())


async def start_wyoming_server(settings: Settings) -> None:
    wyoming_info = build_info(settings)
    server = AsyncServer.from_uri(f'tcp://0.0.0.0:{settings.wyoming_port}')
    handler_factory = partial(WyomingTtsHandler, settings, wyoming_info)
    logger.info(f'Starting Wyoming server on port {settings.wyoming_port}')
    await server.run(handler_factory)
