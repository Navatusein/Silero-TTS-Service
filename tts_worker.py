import os
import torch
import logging
import argparse

from app.config import Settings, models_directory, audios_directory

settings = Settings()
logger = logging.getLogger('uvicorn')

device = torch.device('cpu')
torch.set_num_threads(settings.number_of_threads)

model_file_path = models_directory + settings.silero_settings[settings.language]['model_name']

model = torch.package.PackageImporter(model_file_path).load_pickle('tts_models', 'model')
model.to(device)


def generate_audio_file(text: str, speaker: str, sample_rate: int, file_path: str, sox_params: str = ''):
    if speaker not in settings.silero_settings[settings.language]['speakers']:
        raise RuntimeError(f'Invalid speaker: speaker {speaker} not supported by this language')
    logger.info(f'Start text processing: {text}')

    temp_file_path = audios_directory + 'temp.wav'

    model.save_wav(ssml_text=text, speaker=speaker, audio_path=temp_file_path, sample_rate=sample_rate)

    command = f'sox ./audios/temp.wav {file_path} {sox_params}'
    os.system(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('TTS Service')
    parser.add_argument('--text', help='Text', type=str, default=None)
    parser.add_argument('--speaker', help='Speaker', type=str, default=None)
    parser.add_argument('--sample_rate', help='Sample rate', type=int, default=None)
    parser.add_argument('--file_path', help='File path', type=str, default=None)
    parser.add_argument('--sox_params', help='Sox params', type=str, default=None)

    args = parser.parse_args()

    file_path = generate_audio_file(text=args.text, speaker=args.speaker, sample_rate=args.sample_rate,
                                    file_path=args.file_path, sox_params=args.sox_params)

    print(file_path, end='')


