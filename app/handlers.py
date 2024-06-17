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


@lru_cache()
def get_settings():
    return Settings()


@router.get('/')
async def index():
    return {'status': 'work'}


@router.get('/voices', response_class=HTMLResponse)
async def process(settings: Settings = Depends(get_settings)):
    return '\n'.join(settings.silero_settings[settings.language]['speakers'])


@router.get('/process')
async def process(request: Request, settings: Settings = Depends(get_settings)):
    request_args = dict(request.query_params)

    print(request_args)

    speaker = request_args['VOICE']
    text = request_args['INPUT_TEXT']
    text = normalize(text)
    text = f'<speak>{text}</speak>'

    try:
        audio_file = get_audio_file(text=text, speaker=speaker)
        return FileResponse(path=audio_file)
    except RuntimeError as exception:
        logger.error(exception)
        return HTMLResponse(status_code=400)


# noinspection PyRedundantParentheses
@router.post('/process')
async def process(request: Request, settings: Settings = Depends(get_settings)):
    body = await request.body()
    body_decoded = body.decode("utf-8")
    body_args = parse_qs(body_decoded)

    print(body_args)

    speaker = body_args['VOICE'][0]
    text = body_args['INPUT_TEXT'][0]
    text = normalize(text)

    if (settings.ha_fix):
        text = f'{text}<break time="2s"/>'
    
    text = f'<speak>{text}</speak>'

    try:
        audio_file = get_audio_file(text=text, speaker=speaker)
        return FileResponse(path=audio_file, filename=audio_file, media_type='audio/wav')
    except RuntimeError as exception:
        logger.error(exception)
        return HTMLResponse(status_code=400)


@router.get('/settings')
async def show_settings(settings: Settings = Depends(get_settings)):
    settings_dict = settings.dict()
    del settings_dict['silero_settings']
    return PlainTextResponse(json.dumps(settings_dict, indent=2))


@router.get('/clear_cache')
async def clear_cache(settings: Settings = Depends(get_settings)):
    audios_directory = './audios/'
    try:
        for file in os.listdir(audios_directory):
            os.remove(os.path.join(audios_directory, file))

        gc.collect()

        return PlainTextResponse(status_code=200, content='Success')
    except Exception as e:
        logger.error(e)
        return PlainTextResponse(status_code=400, content='Error')


