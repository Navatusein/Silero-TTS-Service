import json
import logging
import os
import torch

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger('uvicorn')
models_directory = './models/'
audios_directory = './audios/'
version = '2.0.0'


class Settings(BaseSettings):
    number_of_threads: int = 4
    language: str = 'ru'
    sample_rate: int = 48000
    sox_param: str = ''
    ha_fix: bool = False
    voice_tts_errors: bool = False

    silero_settings: dict = {
        'ru': {
            'model_link': 'https://models.silero.ai/models/tts/ru/v5_1_ru.pt',
            'speakers': [
                'aidar', 'baya', 'kseniya', 'xenia', 'eugene'
            ]
        },
        'uk': {
            'model_link': 'https://models.silero.ai/models/tts/ua/v4_ua.pt',
            'speakers': [
                'mykyta', 'random'
            ]
        },
        'multi': {
            'model_link': 'https://models.silero.ai/models/tts/multi/v2_multi.pt',
            'speakers': [
                'irina', 'random'
            ]
        }
    }

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


def get_model_file(settings: Settings) -> str:
    # The file name comes from the link, so a new model version is downloaded instead of reusing the old file
    return models_directory + os.path.basename(settings.silero_settings[settings.language]['model_link'])


def settings_checker():
    settings = Settings()

    if settings.number_of_threads <= 0:
        logger.error('Invalid settings: number_of_threads can\'t be lower than zero')
        exit(-1)

    if settings.language not in ['uk', 'ru', 'multi']:
        logger.error(f'Invalid settings: language {settings.language} unsupported')
        exit(-1)

    if settings.sample_rate not in [8000, 24000, 48000]:
        logger.error(f'Invalid settings: sample_rate {settings.sample_rate} unsupported')
        exit(-1)

    settings_dict = settings.model_dump()

    del settings_dict['silero_settings']

    if not os.path.exists(models_directory):
        os.mkdir(models_directory)

    local_file = get_model_file(settings)

    if not os.path.exists(local_file):
        url = settings.silero_settings[settings.language]['model_link']
        logger.info(f'Download silero model {local_file}')
        torch.hub.download_url_to_file(url, local_file)

    logger.info(f'Current version: {version}')
    logger.info(f'Settings: {json.dumps(settings_dict)}')


settings_checker()
