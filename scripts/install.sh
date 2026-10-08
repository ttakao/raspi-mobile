#!/bin/sh
set -eu
[ "$(id -u)" -eq 0 ] || { echo 'sudo sh scripts/install.sh で実行してください'; exit 1; }
base=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ -d /sys/class/vtconsole ] || { echo 'Pi上で実行してください'; exit 1; }
apt-get update
apt-get install -y python3 kbd console-setup-linux bluez avahi-daemon
font=/usr/share/consolefonts/Lat15-Terminus20x10.psf.gz
[ -f "$font" ] || { echo "フォントがありません: $font"; exit 1; }
backup=/var/backups/raspi-mobile/$(date +%Y%m%d-%H%M%S)
mkdir -p "$backup" /usr/local/lib/raspi-mobile
for f in /usr/local/sbin/mhs-console-start /etc/systemd/system/mhs-console.service; do
    if [ -f "$f" ]; then cp "$f" "$backup/"; fi
done
install -m 644 "$base/scripts/mhs-console.py" /usr/local/lib/raspi-mobile/mhs-console.py
install -m 755 "$base/scripts/keyboard.py" /usr/local/bin/mobile-keyboard
install -m 644 "$base/systemd/mhs-console.service" /etc/systemd/system/mhs-console.service
systemctl daemon-reload
systemctl enable --now bluetooth avahi-daemon
systemctl enable mhs-console.service
systemctl restart mhs-console.service
systemctl --no-pager -l status mhs-console.service
echo "バックアップ: $backup"
