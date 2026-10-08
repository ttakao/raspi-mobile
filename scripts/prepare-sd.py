#!/usr/bin/env python3
"""Prepare mounted FAT boot partition on Mac, preserving cmdline.txt exactly."""
import argparse
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK = '\n[all]\n# raspi-mobile: MHS console\ndtparam=spi=on\ndtoverlay=mhs35:rotate=90\n'

def prepare(boot):
    config = boot / 'config.txt'
    if not config.is_file() or not (boot / 'overlays').is_dir():
        raise SystemExit('config.txtとoverlaysがあるbootfsを指定してください。')
    text = config.read_text()
    existing = [line.strip() for line in text.splitlines()
                if line.strip().startswith('dtoverlay=mhs35')]
    if existing and any(line != 'dtoverlay=mhs35:rotate=90' for line in existing):
        raise SystemExit('既存のMHS設定が異なります。自動上書きせず確認してください。')
    backup = boot / 'config.txt.before-raspi-mobile'
    if not backup.exists():
        shutil.copy2(config, backup)
    if not existing:
        config.write_text(text + BLOCK)
    shutil.copy2(ROOT / 'vendor/mhs35.dtbo', boot / 'overlays/mhs35.dtbo')
    dest = boot / 'raspi-mobile'
    dest.mkdir(exist_ok=True)
    for folder in ['scripts', 'systemd', 'vendor']:
        shutil.copytree(ROOT / folder, dest / folder, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(ROOT / 'README.md', dest / 'README.md')
    print('準備完了。cmdline.txtは変更していません。安全に取り外してPiを起動してください。')
    print('初回はMacからSSHし、sudo sh /boot/firmware/raspi-mobile/scripts/install.sh を実行します。')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('boot', type=pathlib.Path, help='例: /Volumes/bootfs')
    prepare(parser.parse_args().boot)
