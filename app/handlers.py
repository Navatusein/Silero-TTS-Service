import gc
import logging
import json
import os

from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from urllib.parse import parse_qs
from functools import lru_cache

from app.normalizer import normalize
from app.config import Settings
from app.tts import get_audio_file

logger = logging.getLogger('uvicorn')
router = APIRouter()

error_texts = {
    'ru': 'Ошибка синтеза речи.',
    'uk': 'Помилка синтезу мовлення.',
    'multi': 'Ошибка синтеза речи.',
}


@lru_cache()
def get_settings():
    return Settings()


def get_tts_args(args: dict) -> tuple[str, str] | None:
    args = {key.lower(): value for key, value in args.items()}

    speaker = args.get('voice')
    text = args.get('input_text', args.get('text'))

    if not speaker or not text:
        return None

    return speaker, text


def error_response(settings: Settings, speaker: str | None, message: str):
    logger.error(message)

    if settings.voice_tts_errors:
        speakers = settings.silero_settings[settings.language]['speakers']
        error_speaker = speaker if speaker in speakers else speakers[0]

        try:
            audio_file = get_audio_file(text=f'<speak>{error_texts[settings.language]}</speak>', speaker=error_speaker)
            return FileResponse(path=audio_file, media_type='audio/wav')
        except RuntimeError as exception:
            logger.error(f'Failed to voice the error: {exception}')

    return PlainTextResponse(status_code=400, content=message)


@router.get('/')
async def index():
    return {'status': 'work'}


@router.get('/voices', response_class=HTMLResponse)
async def process(settings: Settings = Depends(get_settings)):
    return '\n'.join(settings.silero_settings[settings.language]['speakers'])


@router.get('/process')
async def process(request: Request, settings: Settings = Depends(get_settings)):
    tts_args = get_tts_args(dict(request.query_params))

    if tts_args is None:
        return error_response(settings, None, 'Parameters VOICE and INPUT_TEXT are required')

    speaker, text = tts_args
    text = normalize(text)
    text = f'<speak>{text}</speak>'

    try:
        audio_file = get_audio_file(text=text, speaker=speaker)
        return FileResponse(path=audio_file)
    except RuntimeError as exception:
        return error_response(settings, speaker, str(exception))


# noinspection PyRedundantParentheses
@router.post('/process')
async def process(request: Request, settings: Settings = Depends(get_settings)):
    body = await request.body()
    body_decoded = body.decode("utf-8")
    body_args = {key: values[0] for key, values in parse_qs(body_decoded).items()}

    tts_args = get_tts_args(body_args)

    if tts_args is None:
        return error_response(settings, None, 'Parameters VOICE and INPUT_TEXT are required')

    speaker, text = tts_args
    text = normalize(text)

    if (settings.ha_fix):
        text = f'{text}<break time="2s"/>'
    
    text = f'<speak>{text}</speak>'

    try:
        audio_file = get_audio_file(text=text, speaker=speaker)
        return FileResponse(path=audio_file, filename=audio_file, media_type='audio/wav')
    except RuntimeError as exception:
        return error_response(settings, speaker, str(exception))


@router.get('/settings')
async def show_settings(settings: Settings = Depends(get_settings)):
    settings_dict = settings.model_dump()
    del settings_dict['silero_settings']
    return PlainTextResponse(json.dumps(settings_dict, indent=2))


@router.get('/clear_cache')
async def clear_cache(settings: Settings = Depends(get_settings)):
    audios_directory = './audios/'
    try:
        # The cache directory is created on the first synthesis, so it may not exist yet
        os.makedirs(audios_directory, exist_ok=True)

        for file in os.listdir(audios_directory):
            os.remove(os.path.join(audios_directory, file))

        gc.collect()

        return PlainTextResponse(status_code=200, content='Success')
    except Exception as e:
        logger.error(e)
        return PlainTextResponse(status_code=400, content='Error')


