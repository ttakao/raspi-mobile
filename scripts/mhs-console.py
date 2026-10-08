#!/usr/bin/env python3
"""Bind tty1 directly through the LCD device; fb0 need not exist."""
import fcntl
import pathlib
import struct
import subprocess
import time

FONT = '/usr/share/consolefonts/Lat15-Terminus20x10.psf.gz'
def main():
    for _ in range(30):
        for fb in pathlib.Path('/sys/class/graphics').glob('fb[0-9]*'):
            if 'ili9486' not in (fb / 'name').read_text():
                continue
            device = pathlib.Path('/dev') / fb.name
            if not device.exists():
                continue
            for vt in pathlib.Path('/sys/class/vtconsole').glob('vtcon*'):
                if 'frame buffer device' in (vt / 'name').read_text():
                    (vt / 'bind').write_text('1\n')
            # linux/fb.h: FBIOPUT_CON2FBMAP; struct fb_con2fbmap = two u32.
            with device.open('rb', buffering=0) as stream:
                fcntl.ioctl(stream.fileno(), 0x4610,
                            struct.pack('=II', 1, int(fb.name[2:])))
            blank = fb / 'blank'
            if blank.exists():
                blank.write_text('0\n')
            subprocess.run(['chvt', '1'], check=True)
            subprocess.run(['setfont', '-C', '/dev/tty1', FONT], check=True)
            with open('/dev/tty1', 'wb', buffering=0) as tty:
                tty.write(b'\x1b[9;0]\x1b[13]')
            print(f'tty1 -> {device}; font: {FONT}')
            return
        time.sleep(1)
    raise SystemExit('ILI9486 LCD not found after 30 seconds')
if __name__ == '__main__':
    main()
