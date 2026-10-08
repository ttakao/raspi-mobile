#!/usr/bin/env python3
"""Discover keyboards by name, then pair/trust/connect selected device."""
import re
import subprocess

def run(*args, check=True, capture=False):
    return subprocess.run(['bluetoothctl', *args], check=check,
                          text=True, capture_output=capture)

def parse_devices(text):
    return re.findall(r'^Device ([0-9A-Fa-f:]{17}) (.+)$', text, re.M)

def main():
    run('power', 'on')
    print('キーボードをペアリングモードにしてください。15秒スキャンします。', flush=True)
    # A timeout ends scanning; its exit code is not used as proof of discovery.
    run('--timeout', '15', 'scan', 'on', check=False)
    run('scan', 'off', check=False)
    devices = parse_devices(run('devices', capture=True).stdout)
    if not devices:
        raise SystemExit('機器が見つかりません。ペアリングモードを確認して再実行してください。')
    print('既に登録された機器も含まれます。名前を確認してください。')
    for i, (mac, name) in enumerate(devices, 1):
        print(f'{i}: {name} [{mac}]')
    answer = input('接続する番号（空欄で中止）: ').strip()
    if not answer:
        return
    if not answer.isdecimal() or not 1 <= int(answer) <= len(devices):
        raise SystemExit('番号が範囲外です。')
    mac, name = devices[int(answer)-1]
    info = run('info', mac, capture=True).stdout
    if not re.search(r'Paired:\s+yes', info):
        print('表示されたPINはBluetoothキーボードで入力してEnter。確認質問には内容を確認して応答してください。', flush=True)
        run('--agent', 'KeyboardDisplay', '--timeout', '90', 'pair', mac)
    run('trust', mac)
    run('connect', mac)
    run('info', mac)
    print(f'{name}: Piの液晶側で入力を試してください。')
if __name__ == '__main__':
    main()
