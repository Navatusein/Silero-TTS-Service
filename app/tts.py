import time
import hashlib
import os
import subprocess
import logging

from app.config import Settings, audios_directory

logger = logging.getLogger('uvicorn')
settings = Settings()


def get_audio_file(text: str, speaker: str, file_extension: str = 'wav') -> str:
    text_hash = hashlib.sha512(bytes(text, 'UTF-8')).hexdigest()
    file_path = audios_directory + speaker + '-' + text_hash + '.' + file_extension

    if not os.path.exists(audios_directory):
        os.mkdir(audios_directory)

    if os.path.exists(file_path):
        return file_path

    start_time = time.time()
    result = subprocess.run(args=['python3',
                                  'tts_worker.py',
                                  f'--text={text}',
                                  f'--speaker={speaker}',
                                  f'--sample_rate={settings.sample_rate}',
                                  f'--file_path={file_path}',
                                  f'--sox_params={settings.sox_param}'
                                  ],
                            capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8"))

    elapsed_time = time.time() - start_time
    logger.info(f'Time spent on the process: {elapsed_time}')

    return file_path
