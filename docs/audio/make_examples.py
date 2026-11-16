"""Builds the audio examples from examples.json: MP3 files for the repository and videos for the README players.

Usage: python docs/audio/make_examples.py [name ...]. See README.md next to this file.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

audio_directory = Path(__file__).resolve().parent
root_directory = audio_directory.parents[1]
video_directory = audio_directory / 'video'
examples_file = audio_directory / 'examples.json'

sample_rate = 48000

# GitHub dark theme colors, so the player blends into the README page
background_color = '0x0d1117'
wave_color = '0x58a6ff'
subtitle_color = '0x8b949e'

default_title_font = 'C:/Windows/Fonts/segoeuib.ttf'
default_subtitle_font = 'C:/Windows/Fonts/segoeui.ttf'


def synthesize(examples: list[dict], output_directory: Path):
    # The service reads the language on import, so this runs in a separate process for each language
    sys.path.insert(0, str(root_directory))
    os.chdir(root_directory)

    import torch
    from app.config import Settings, get_model_file
    from app.normalizer import normalize

    model = torch.package.PackageImporter(get_model_file(Settings())).load_pickle('tts_models', 'model')

    for example in examples:
        text = normalize(example['text'])
        print(f'{example["name"]}: {text}')
        model.save_wav(ssml_text=f'<speak>{text}</speak>', speaker=example['voice'],
                       audio_path=str(output_directory / f'{example["name"]}.wav'), sample_rate=sample_rate)


def filter_path(path: Path | str) -> str:
    # Filter options are separated by ":", so the drive letter colon on Windows is escaped
    return "'" + Path(path).as_posix().replace(':', '\\:') + "'"


def make_video(example: dict, audio_file: Path, video_file: Path, temp_directory: Path, fonts: tuple[str, str]):
    # Text goes through files, so titles with quotes and colons need no escaping
    title_file = temp_directory / f'{example["name"]}-title.txt'
    subtitle_file = temp_directory / f'{example["name"]}-subtitle.txt'
    title_file.write_text(example['title'], encoding='utf-8')
    subtitle_file.write_text(f'Silero TTS Service  ·  {example["voice"]}', encoding='utf-8')

    video_filter = (
        f'color=c={background_color}:s=1280x360:r=30[background];'
        f'[0:a]showwaves=s=1280x190:mode=cline:rate=30:scale=sqrt:draw=full:colors={wave_color},format=rgba[wave];'
        f'[background][wave]overlay=0:145:shortest=1:format=auto,'
        f'drawtext=fontfile={filter_path(fonts[0])}:textfile={filter_path(title_file)}'
        f':fontcolor=white:fontsize=48:x=56:y=40,'
        f'drawtext=fontfile={filter_path(fonts[1])}:textfile={filter_path(subtitle_file)}'
        f':fontcolor={subtitle_color}:fontsize=26:x=56:y=104,'
        f'format=yuv420p[video]'
    )

    run_ffmpeg('-i', audio_file, '-filter_complex', video_filter, '-map', '[video]', '-map', '0:a',
               '-c:v', 'libx264', '-c:a', 'aac', '-ar', str(sample_rate), '-ac', '1', video_file)


def run_ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description='Build audio examples for the README')
    parser.add_argument('names', nargs='*', help='Examples to build, all by default')
    parser.add_argument('--title-font', default=default_title_font, help='Bold font for the video title')
    parser.add_argument('--subtitle-font', default=default_subtitle_font, help='Regular font for the video subtitle')
    parser.add_argument('--synthesize', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    examples = json.loads(examples_file.read_text(encoding='utf-8'))
    unknown_names = set(args.names) - {example['name'] for example in examples}

    if unknown_names:
        parser.error(f'unknown examples: {", ".join(sorted(unknown_names))}')

    examples = [example for example in examples if not args.names or example['name'] in args.names]

    if args.synthesize:
        synthesize(examples, args.synthesize)
        return

    for font in (args.title_font, args.subtitle_font):
        if not Path(font).exists():
            parser.error(f'font {font} not found, pass it with --title-font and --subtitle-font')

    video_directory.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_directory:
        temp_directory = Path(temp_directory)

        for language in sorted({example['language'] for example in examples}):
            names = [example['name'] for example in examples if example['language'] == language]
            subprocess.run([sys.executable, __file__, '--synthesize', str(temp_directory), *names],
                           env={**os.environ, 'LANGUAGE': language}, check=True)

        for example in examples:
            audio_file = audio_directory / f'{example["name"]}.mp3'
            video_file = video_directory / f'{example["name"]}.mp4'

            run_ffmpeg('-i', temp_directory / f'{example["name"]}.wav', '-ac', '1', '-ar', sample_rate, '-b:a', '96k',
                       audio_file)
            make_video(example, audio_file, video_file, temp_directory, (args.title_font, args.subtitle_font))
            print(f'{audio_file.relative_to(root_directory)}, {video_file.relative_to(root_directory)}')


if __name__ == '__main__':
    main()
