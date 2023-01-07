import json
import logging
import os
import torch

from pydantic import BaseSettings

logger = logging.getLogger('uvicorn')
models_directory = './models/'
audios_directory = './audios/'
version = '1.0.0'


class Settings(BaseSettings):
    number_of_threads: int = 4
    language: str = 'ru'
    sample_rate: int = 48000
    sox_param: str = ''
    ha_fix: bool = False

    silero_settings = {
        'ru': {
            'model_link': 'https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
            'model_name': 'ru_model.pt',
            'speakers': [
                'aidar', 'baya', 'kseniya', 'xenia', 'eugene', 'random'
            ]
        },
        'uk': {
            'model_link': 'https://models.silero.ai/models/tts/ua/v3_ua.pt',
            'model_name': 'uk_model.pt',
            'speakers': [
                'mykyta', 'random'
            ]
        }
    }

    class Config:
        env_file = ".env"


def settings_checker():
    settings = Settings()

    if settings.number_of_threads <= 0:
        logger.error('Invalid settings: number_of_threads can\'t be lower than zero')
        exit(-1)

    if settings.language not in ['uk', 'ru']:
        logger.error(f'Invalid settings: language {settings.language} unsupported')
        exit(-1)

    if settings.sample_rate not in [8000, 24000, 48000]:
        logger.error(f'Invalid settings: sample_rate {settings.sample_rate} unsupported')
        exit(-1)

    settings_dict = settings.dict()

    del settings_dict['silero_settings']

    if not os.path.exists(models_directory):
        os.mkdir(models_directory)

    model_name = settings.silero_settings[settings.language]['model_name']
    local_file = models_directory + model_name

    if not os.path.exists(local_file):
        url = settings.silero_settings[settings.language]['model_link']
        logger.info(f'Download silero model {local_file}')
        torch.hub.download_url_to_file(url, local_file)

    logger.info(f'Current version: {version}')
    logger.info(f'Settings: {json.dumps(settings_dict)}')


settings_checker()
