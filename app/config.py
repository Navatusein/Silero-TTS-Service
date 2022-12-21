import logging

from pydantic import BaseSettings


logger = logging.getLogger('uvicorn')


class Settings(BaseSettings):
    number_of_threads: int = 4
    language: str = 'ru'
    sample_rate: int = 48000
    sox_param: str = ''
    ha_fix: bool = False
    sls_fix: bool = False

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


settings_checker()
