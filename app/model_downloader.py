import torch
import os

from app.config import Settings

settings = Settings()
local_path = './data/'


def get_model_path() -> str:
    if not os.path.exists(local_path):
        os.mkdir('data')

    model_name = settings.silero_settings[settings.language]['model_name']

    local_file = local_path + model_name

    if not os.path.exists(local_file):
        url = settings.silero_settings[settings.language]['model_link']
        torch.hub.download_url_to_file(url, local_file)

    return local_file
