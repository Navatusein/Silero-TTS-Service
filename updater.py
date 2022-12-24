import requests
import os
import shutil
import logging

from zipfile import ZipFile

logger = logging.getLogger(__name__)
file_version_url = 'https://raw.githubusercontent.com/Navatusein/Silero-TTS-Service/main/version'
file_requirements_url = 'https://raw.githubusercontent.com/Navatusein/Silero-TTS-Service/main/requirements.txt'
update_url = 'https://github.com/Navatusein/Silero-TTS-Service/archive/refs/heads/main.zip'


def copy(source: str, destination: str):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            path_file = root.replace(source, '').lstrip(os.sep)
            destination_path = os.path.join(destination, path_file)

            if not os.path.isdir(destination_path):
                os.makedirs(destination_path)

            shutil.copyfile(os.path.join(root, file), os.path.join(destination_path, file))


def update(requirements_update: bool):
    logger.info(f'Starting updating')
    update_request = requests.get(update_url, allow_redirects=True)

    if not os.path.exists('./data'):
        os.makedirs('./data')

    open('./data/latest_version.zip', 'wb').write(update_request.content)

    with ZipFile('./data/latest_version.zip') as file:
        file_name = file.filelist[0].filename
        file.extractall('./data/')

    copy(f'./data/{file_name}/', f'{os.getcwd()}')

    if requirements_update:
        logger.info('Update requirements')
        os.system(f'pip install -r requirements.txt')

    path_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), './data/latest_version.zip')
    os.remove(path_file)

    path_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'./data/{file_name}')
    shutil.rmtree(path_file)


def check_for_available_update() -> [bool, bool]:
    if not os.path.exists('./version'):
        return True, True

    version_file = open('./version', 'r')
    version = version_file.readline()

    logger.info(f'Silero TTS Service version: {version}')

    version_request = requests.get(file_version_url)
    latest_version = version_request.text

    code_update = False

    if latest_version != version:
        code_update = True

    requirements_update = True

    if os.path.exists('./requirements.txt'):
        requirements_file = open('./requirements.txt', 'r')
        requirements = requirements_file.read()

        requirements_request = requests.get(file_requirements_url)
        latest_requirements = requirements_request.text

        if requirements == latest_requirements:
            requirements_update = False

    return code_update, requirements_update


if __name__ == '__main__':
    log_format = u'%(levelname)s [%(asctime)s] %(message)s'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        encoding='UTF-8'
    )

    require_update, require_requirements_update = check_for_available_update()

    if require_update:
        update(require_requirements_update)
        logger.info('Update success')
        os.system('python3 updater.py')
        exit(0)

    os.system('python3 main.py')

