import os
import torch
import hashlib

from app.config import Settings
from app.model_downloader import get_model_path

settings = Settings()

device = torch.device('cpu')
torch.set_num_threads(settings.number_of_threads)

model_file_path = get_model_path()
audios_directory = './audios/'

model = torch.package.PackageImporter(model_file_path).load_pickle('tts_models', 'model')
model.to(device)


def get_tts_file(text: str, speaker: str, sample_rate: int, sox_params: str = '', file_extension: str = 'wav') -> str:
    text_hash = hashlib.sha512(bytes(text, 'UTF-8')).hexdigest()
    audio_file_path = audios_directory + speaker + '-' + text_hash + '.' + file_extension

    if not os.path.exists(audios_directory):
        os.mkdir(audios_directory)

    if os.path.exists(audio_file_path):
        return audio_file_path

    temp_file_path = audios_directory + 'temp.wav'

    model.save_wav(ssml_text=text, speaker=speaker, audio_path=temp_file_path, sample_rate=sample_rate)

    command = f'sox ./audios/temp.wav {audio_file_path} {sox_params}'
    os.system(command)

    return audio_file_path
