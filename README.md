# raspi-mobile：Zero 2 W 携帯SSH端末

対象：Raspberry Pi Zero 2 W、Raspberry Pi OS Lite 32bit / Raspbian 13.6 (Trixie)、MHS-3.5inch SPI液晶（ILI9486、480×320）、Bluetoothキーボード。

## 確認できていることと今回の改善

2026-10-08、実機で液晶表示・Bluetoothキーボードでのログイン・SSH接続を確認。20pxの `Lat15-Terminus20x10` が読みやすいというユーザー判断。
HDMIなしでは `/proc/fb` に `1 fb_ili9486` だけが現れた。con2fbmapは内部で/dev/fb0を開くため失敗し、さらにframe buffer deviceのbindが0だった。bindを1にして表示は復旧した。

今回保存したコードは、液晶の実デバイスを直接開いてLinuxのFBIOPUT_CON2FBMAPを実行する。/dev/fb0の仮のシンボリックリンクやcmdline.txtの変更は不要。サービスの実行順をconsole-setupの後にし、フォント上書きを避ける。

**会話中に動いた手順と、ここで改善したコードは区別する。この一式はMacで構文・模擬デバイス・SD準備処理を検証済み。新しい直接ioctl方式、キーボード選択ツール、SD初期構築は実機で未検証。導入後はHDMIなしの再起動確認を行う。**

## 新しいmicroSDをHDMIなしで準備

1. Raspberry Pi ImagerでZero 2 W / Raspberry Pi OS Lite (32-bit)を選ぶ。
2. ホスト名 `raspi-zero2`、ユーザー名、パスワード、Wi-Fi（2.4GHz）、国JP、タイムゾーンAsia/Tokyo、SSHを設定して書き込む。
3. Imagerが取り外したカードをMacへ挿し直し、Finderでbootfsが見えることを確認。
4. Macのターミナルで実行：

```sh
python3 ~/dev/raspi-mobile/scripts/prepare-sd.py /Volumes/bootfs
```

この操作はconfig.txtをバックアップし、MHS設定の追記・overlay配置・セットアップファイルのコピーを行う。**cmdline.txtは一切変更しない。** bootfs名が違う場合はFinderの名前に合わせる。

5. カードを安全に取り外す。Piの電源が抜けている状態で液晶を取り付け、カードを挿して起動。HDMIは不要。まだ液晶が黒くても、初回セットアップ前なのでそのままSSHする。
6. Macから接続：

```sh
ssh tsukasa@raspi-zero2.local
```

ユーザー名とホスト名はImagerで指定したものを使う。.localが使えなければルーターの接続端末一覧でIPを確認して `ssh tsukasa@IPアドレス`。

7. **PiのSSH画面で**実行（インターネット接続が必要）：

```sh
sudo sh /boot/firmware/raspi-mobile/scripts/install.sh
```

8. active (exited)、status=0/SUCCESSと液晶表示を確認し、`sudo reboot`。HDMIを挿さず、液晶のログイン画面と20pxフォントを確認する。

### 「Imagerの後、ファイル編集だけ」の範囲

Macから見えるFATパーティションにはoverlayとconfig.txtを配置できる。一方、サービス・フォント・BluetoothツールはLinux側の領域へ導入が必要。**この手順はHDMI不要だが、初回SSHで1コマンド実行する。完全なファイル編集だけの無操作セットアップではない。** Imagerが作成する初回起動処理やcmdlineを上書きする方法は採用しない。

## 今動いているPiへ導入する場合（カード再作成不要）

Macで実行：

```sh
scp -r ~/dev/raspi-mobile tsukasa@raspi-zero2.local:~/
ssh tsukasa@raspi-zero2.local
```

Piで：

```sh
sudo sh ~/raspi-mobile/scripts/install.sh
sudo reboot
```

既存のMHS overlay設定はそのまま利用。install.shはconfig.txt/cmdline.txtを変更しない。旧サービスとスクリプトは `/var/backups/raspi-mobile/日時/` へ保存する。

## Bluetooth：キーボードを名前で選んで登録

PiへSSHした画面で：

```sh
sudo mobile-keyboard
```

1. キーボードをBluetoothモード・ペアリングモードにする。
2. 15秒間スキャン後、一覧の名前を見て番号を入力。MACを手入力する必要はない。
3. PINが表示されたら、**Bluetoothキーボードで数字を入力してEnter**。確認質問は画面に従う。
4. ツールがpair → trust → connectを実行。最後のinfoでPaired/Trusted/Connected: yesを確認。
5. 入力はMacのSSH画面ではなく、Piの液晶コンソールへ届く。

一覧には以前登録した機器やキーボード以外も含まれる。名前を確認して選ぶ。キーボードを追加しても古い登録は自動削除しない。畳んで電源OFF→ON、キーを押して再接続するか確認する。trustは再接続を許可する設定で、機種ごとの自動再接続を保証するものではない。

既存の登録の確認・削除：

```text
bluetoothctl
 devices
 info AA:BB:CC:DD:EE:FF
 remove AA:BB:CC:DD:EE:FF
 quit
```

removeは指定した機器だけ登録解除する。ペアリングに失敗した場合は出力を確認し、必要な機器のみ解除して再試行する。

## Wi-Fi

```sh
nmcli device status
nmcli device wifi list
sudo nmcli --ask device wifi connect "SSID"
ip -4 addr show wlan0
```

スマホのテザリングも2.4GHzを選ぶ。パスワードはコマンドに書かず質問に入力する。

## 画面が黒い場合

```sh
cat /proc/fb
systemctl status mhs-console.service --no-pager -l
journalctl -u mhs-console.service -b --no-pager
cat /sys/class/vtconsole/vtcon*/name
cat /sys/class/vtconsole/vtcon*/bind
sudo dmesg | grep -Ei 'ili|fbtft|fbcon|spi'
sudo systemctl restart mhs-console.service
```

fb_ili9486がなければoverlayと物理接続を確認。差し直しは必ずpoweroffして電源を抜いてから。サービス成功でも表示の実確認は必要。
液晶への直接テスト（色ノイズが出る。画面内容のみ一時変更）：

```sh
sudo dd if=/dev/urandom of=/dev/fb1 bs=307200 count=1
sudo systemctl restart mhs-console.service
```

デバイス番号は必ず/proc/fbで確認。以前のsetterm --powersaveでのioctlエラー、/dev/fb0へのリンク作成は新コードでは不要。

## フォント

標準は20px、480×320で約48文字×16行。変更するなら `/usr/local/lib/raspi-mobile/mhs-console.py` のFONTを変更しサービスを再起動。候補は `ls /usr/share/consolefonts/*Terminus*` で確認。

## 復元

サービスだけ止める場合：

```sh
sudo systemctl disable --now mhs-console.service
```

旧設定に戻す場合、インストール時に表示されたバックアップ内のmhs-console.serviceと旧mhs-console-startを元の場所に戻し、daemon-reload、サービス再起動。旧方式はHDMIなしで失敗した条件があるため、その点を考慮する。
SD準備のconfig.txt変更を戻す場合は、他の変更を失わないよう現状を保存してからconfig.txt.before-raspi-mobileを確認する。

## 出典・同梱ファイル

- MHS仕様・配布元：https://www.lcdwiki.com/MHS-3.5inch_RPi_Display
- overlay出典：https://github.com/goodtft/LCD-show
- 同梱overlayの固定コミット：a36c00a55e11f0de3b4be0e66f0a2cec47076e23、usr/mhs35-overlay.dtb
- Raspberry Pi config.txt：https://www.raspberrypi.com/documentation/computers/config_txt.html
- Linux fbcon：https://docs.kernel.org/fb/fbcon.html
- Linux fb ioctl：https://github.com/torvalds/linux/blob/master/include/uapi/linux/fb.h
- BlueZ bluetoothctl：https://github.com/bluez/bluez/blob/master/client/bluetoothctl.rst

メーカー一括インストーラーは使用しない。同梱overlayは上流のバイナリそのまま。再配布時は上流のライセンス条件を別途確認する。
