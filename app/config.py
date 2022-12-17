from pydantic import BaseSettings


class Settings(BaseSettings):
    number_of_threads: int = 4
    language: str = 'ru'
    speaker: str = 'xenia'
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
