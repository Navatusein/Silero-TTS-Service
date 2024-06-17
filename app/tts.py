import time
import hashlib
import os
import subprocess
import logging
import torch
import argparse

from app.config import Settings, audios_directory, models_directory

settings = Settings()
logger = logging.getLogger('uvicorn')

device = torch.device('cpu')
torch.set_num_threads(settings.number_of_threads)

model_file_path = models_directory + settings.silero_settings[settings.language]['model_name']

model = torch.package.PackageImporter(model_file_path).load_pickle('tts_models', 'model')
model.to(device)


def generate_speach(text: str, speaker: str, sample_rate: int,
                    file_path: str, sox_params: str = '', volume: float = 1) -> bool:
    temp_file_path = audios_directory + 'temp.wav'

    torch.no_grad()
    model.save_wav(ssml_text=text, speaker=speaker, audio_path=temp_file_path, sample_rate=sample_rate)

    command = f'sox -v {volume} ./audios/temp.wav {file_path} {sox_params}'
    os.system(command)

    return True


def get_audio_file(text: str, speaker: str, file_extension: str = 'wav') -> str:
    text_hash = hashlib.sha512(bytes(text, 'UTF-8')).hexdigest()
    file_path = audios_directory + speaker + '-' + text_hash + '.' + file_extension

    if not os.path.exists(audios_directory):
        os.mkdir(audios_directory)

    if os.path.exists(file_path):
        return file_path

    if speaker not in settings.silero_settings[settings.language]['speakers']:
        raise RuntimeError(f'Invalid speaker: speaker {speaker} not supported by this language')

    logger.info(f'Start text processing: {text}')

    start_time = time.time()

    # result = subprocess.run(args=['python3',
    #                               'tts_worker.py',
    #                               f'--text={text}',
    #                               f'--speaker={speaker}',
    #                               f'--sample_rate={settings.sample_rate}',
    #                               f'--file_path={file_path}',
    #                               f'--sox_params={settings.sox_param}'
    #                               ],
    #                         capture_output=True)
    #
    # if result.returncode != 0:
    #     raise RuntimeError(result.stderr.decode("utf-8"))

    generate_speach(text=text, speaker=speaker, sample_rate=settings.sample_rate, file_path=file_path,
                    sox_params=settings.sox_param)

    elapsed_time = time.time() - start_time
    logger.info(f'Time spent on the process: {elapsed_time}')

    return file_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser('TTS Service')
    parser.add_argument('--text', help='Text', type=str, default=None)
    parser.add_argument('--speaker', help='Speaker', type=str, default=None)
    parser.add_argument('--sample_rate', help='Sample rate', type=int, default=None)
    parser.add_argument('--file_path', help='File path', type=str, default=None)
    parser.add_argument('--sox_params', help='Sox params', type=str, default=None)

    args = parser.parse_args()

    generate_speach(text=args.text, speaker=args.speaker, sample_rate=args.sample_rate, file_path=args.file_path,
                    sox_params=args.sox_params)
