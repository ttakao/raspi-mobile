# raspi-mobile：Zero 2 W モバイル端末

外や喫茶店から仮定においてあるパソコンに接続し、なにかをするということはガジェット好きにはたまらない遊びです。今まで数多くの機器が作られました。しかし、私はイマイチ意欲をそそられないのです。よくよく考えて次のような機器があればいいのにな、と思いました。

- ディスプレイは必要。でもSSHで繋ぐと割り切ったら小さくてもいい。GUIならスマホでいい。

- キーボードは折りたたみキーボードってなぜか、ガジェット市場にいっぱいある。Bluetoothでつながればいい。

- スマホとwifiでテザリングできればいい。

- でも、Linuxは絶対に必要。SSHしたいし、VPNのTailscaleとかがいる。

- 容量の大きい電池駆動がいい。できれば18650電池がいい。なぜならば、余分にもってあるけば容量不足にならない。

異常をふまえて、Raspberry Pi Zero 2 W、Raspberry Pi OS Lite 32bit / Raspbian 13.6 (Trixie)、MHS-3.5inch SPI液晶（ILI9486、480×320）、18650電池x2本、電池ボックス、DCDCコンバータ, 電源トグルスイッチ、Bluetoothキーボードで作ることにした。

## 確認できていることと今回の改善

2026-10-08、実機で液晶表示・Bluetoothキーボードでのログイン・SSH接続を確認。20pxの `Lat15-Terminus20x10` が読みやすいとしています。
構築時にはHDMIディスプレイとUSBキーボードを繋いでいたけれども、HDMIなしで作れるようにしたつもり。

****この一式はMacで構文・模擬デバイス・SD準備処理を検証済み。新しい直接ioctl方式、キーボード選択ツール、SD初期構築は実機で未検証。導入後はHDMIなしの再起動確認を行う。**

## 新しいmicroSDをHDMIなしで準備

~/dev/raspi-mobileにすべてのパッケージがダウンロードされている前提です。

1. Raspberry Pi ImagerでZero 2 W / Raspberry Pi OS Lite (32-bit)を選ぶ。
2. ホスト名（任意）、ユーザー名、パスワード、Wi-Fi（2.4GHz）、国JP、タイムゾーンAsia/Tokyo、SSHを設定して書き込む。
3. Imagerが取り外したカードをMacへ挿し直し、Finderでbootfsが見えることを確認。
4. Macのターミナルで実行：

```sh
python3 ~/dev/raspi-mobile/scripts/prepare-sd.py /Volumes/bootfs
```

この操作はconfig.txtをバックアップし、MHS設定の追記・overlay配置・セットアップファイルのコピーを行う。**cmdline.txtは一切変更しない。** bootfs名が違う場合はFinderの名前に合わせる。

5. カードを安全に取り外す。Piの電源が抜けている状態で液晶を取り付け、カードを挿して起動。HDMIは不要。まだ液晶が黒くても、初回セットアップ前なのでそのままSSHする。
6. Macから接続：

```sh
ssh ユーザー名@ホスト目.local
```

コマンド内の「ユーザー名」「iホスト名」はImagerで指定した値に置き換える。「Wi-Fi AP名」は接続先のSSIDに置き換える。.localが使えなければルーターの接続端末一覧でIPを確認して `ssh ユーザー名@IPアドレス`。

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
scp -r ~/dev/raspi-mobile ユーザー名@ホスト名.local:~/
ssh ユーザー名@ホスト名.local
```

Piで：

```sh
sudo sh ~/raspi-mobile/scripts/install.sh
sudo reboot
```

既存のMHS overlay設定はそのまま利用。install.shはconfig.txt/cmdline.txtを変更しない。旧サービスとスクリプトは `/var/backups/raspi-mobile/日時/` へ保存する。

## Zero W v1.1＋3.5inch RPI LCD V3.0（予備機）

2026-10-13、初代Raspberry Pi Zero W v1.1で、再起動後の液晶表示と液晶側でのログインをユーザーが実機確認。液晶裏面の表記は「HVGA 480x320」「3.5inch RPI LCD V3.0」で、MHSの表記はない。正確なメーカー・型番は未特定。この個体で確認した設定として記録する。

Zero WではRaspberry Pi OS Liteの**32ビット版**を使う。実機所感ではZero 2 Wより大幅に遅く、予備の端末として利用する予定。今回の確認は液晶表示・ログインまでで、この機体のBluetoothキーボード接続は未確認。

### 液晶設定

同梱のprepare-sd.pyはMHS用設定を入れるため、この液晶ではその設定を置き換える必要がある。以下は**Zero WへSSH接続した画面**で実行する。

```sh
sudo cp -a /boot/firmware/config.txt /boot/firmware/config.txt.before-piscreen
sudo nano /boot/firmware/config.txt
```

有効な `[all]` セクションで、既存の `dtoverlay=mhs35:rotate=90` を削除またはコメントアウトし、次の設定にする。MHSとpiscreenを同時に有効にしない。既存の他の設定は残す。

```ini
[all]
dtparam=spi=on
dtoverlay=piscreen,speed=18000000,rotate=90
```

MHS設定ではログ上115 MHzになっていた。この個体はpiscreen・18 MHzで表示を確認した。cmdline.txtの編集は不要。

### コンソール用スクリプト

このリポジトリの修正済みscripts/mhs-console.pyを使用する。新規導入なら前述のinstall.shで導入できる。既に導入済みの場合は、Macから最新版をコピーして更新する。

Macで実行（ユーザー名・ホスト名を置き換える）：

```sh
scp ~/dev/raspi-mobile/scripts/mhs-console.py ユーザー名@ホスト名.local:~/mhs-console.py
ssh ユーザー名@ホスト名.local
```

Zero WへSSH接続した画面で実行：

```sh
sudo cp -a /usr/local/lib/raspi-mobile/mhs-console.py /usr/local/lib/raspi-mobile/mhs-console.py.before-update
sudo install -m 755 ~/mhs-console.py /usr/local/lib/raspi-mobile/mhs-console.py
sudo systemctl restart mhs-console.service
sudo reboot
```

旧スクリプトは `/sys/class/graphics/fb1/blank` への消灯解除の書き込みで `OSError: [Errno 22] Invalid argument` が発生し、フォント設定前に停止した。修正版はこの操作がEINVALの場合だけ処理を続け、その他のエラーは報告する。

### 再起動後の確認

```sh
cat /proc/fb
systemctl status mhs-console.service --no-pager -l
```

実機で確認した結果：

```text
1 fb_ili9486
Active: active (exited)
blank control unsupported; continuing
tty1 -> /dev/fb1; font: /usr/share/consolefonts/Lat15-Terminus20x10.psf.gz
```

HDMI側のfb0がなくても動作する。`blank control unsupported; continuing` は対応しない消灯解除操作を飛ばした通知で、この個体では表示・ログインに支障はなかった。最後に実際の液晶表示とログインを確認する。サービス名は互換性のためmhs-consoleのまま。

## Bluetooth：キーボード登録の手順（手動）

2026-10-12、Pi 4 / Raspberry Pi OS Lite 64bitでiClever IC-BK08の接続を確認した手順。Pythonツールでは登録が維持されない事例があったため、以下を標準手順とする。原因は未確定。

### 1. MacからPiへログイン

Macのターミナルで実行。「ユーザー名」「ホスト名」は自分の設定に置き換える。

```sh
ssh ユーザー名@ホスト名.local
```

行頭がPiのユーザー名・ホスト名になったら、以後のコマンドはPi上で実行される。

### 2. Bluetoothを準備

PiへSSHした画面で実行：

```sh
sudo apt install bluez
sudo rfkill unblock bluetooth
sudo systemctl enable --now bluetooth
sudo bluetoothctl
```

以後は同じbluetoothctlを開いたまま操作する。

```text
power on
agent KeyboardDisplay
default-agent
scan on
```

### 3. キーボードを検出

キーボードをペアリングモードにする。複数の接続先を切り替える機種ではPi用の接続先を選ぶ。ペアリングモードの操作は機種の説明書に従う。

画面に次のような表示が出るまで待つ：

```text
[NEW] Device AA:BB:CC:DD:EE:FF キーボード名
```

最初はアドレスだけが出て、後からNameにキーボード名が表示される場合もある。`devices`でも一覧を確認できる。
**目的の名前に対応するアドレスを控える。以後のAA:BB:CC:DD:EE:FFをその値に置き換える。scan offはまだ実行しない。**

### 4. 信頼・ペアリング・接続

同じbluetoothctl内で、順に実行：

```text
trust AA:BB:CC:DD:EE:FF
pair AA:BB:CC:DD:EE:FF
```

PINが表示されたら、接続するBluetoothキーボードで数字を入力してEnterを押す。PINなしで成功する機種もある。確認質問は表示内容を確認して応答する。

`Pairing successful`が出たら続ける：

```text
trust AA:BB:CC:DD:EE:FF
connect AA:BB:CC:DD:EE:FF
info AA:BB:CC:DD:EE:FF
```

次の3項目を確認：

```text
Paired: yes
Trusted: yes
Connected: yes
```

揃ったら終了：

```text
scan off
quit
```

**Bluetoothキーボードの入力はPiの液晶側へ届く。MacのSSH画面には入力されない。** 液晶側でログインして確認する。

### 5. 普段の使用とキーボード交換

登録後は、畳む→開く→キーを押す、で再接続するか確認する。Piの再起動後も試す。通常の再接続でpairを繰り返す必要はない。自動再接続はキーボード側の動作にも依存する。

別のキーボードへ変更するときは、新しいキーボードについて手順2〜4を行う。古い登録を消す必要はない。不要になった機器だけ、bluetoothctl内で次を実行して解除できる：

```text
remove AA:BB:CC:DD:EE:FF
```

### 困ったとき

- `Device ... not available`：現在の一覧に機器がない。scan onを実行し、キーボードをペアリングモードにして、名前と現在のアドレスが表示されてからtrustする。
- `Failed to set power on`：quitで終了し、Piのシェルで `sudo rfkill unblock bluetooth`、`sudo systemctl restart bluetooth` を実行して手順2から再試行。それでも失敗する場合は `rfkill list` と `sudo journalctl -u bluetooth -b --no-pager -n 40` を確認。
- ペアリング成功後にPaired: noへ戻る：登録は完了していない。同じbluetoothctl内で再検出してやり直す。繰り返す場合はログを保存して原因を調べる。
- Connected: yesだが入力できない：Piの液晶側で確認しているか、キーボードの接続先がPiになっているかを確認。

## Wi-Fi

### nmcliで接続先APを追加する

以下は**Piの液晶側でログインした画面、またはPiへSSH接続した画面**で実行する。まず周囲のAPを一覧表示する。

```sh
nmcli device wifi list
```

一覧のSSIDから接続したいAP名を確認する。見つからない場合は再スキャンする。

```sh
sudo nmcli device wifi rescan
nmcli device wifi list
```

次の「Wi-Fi AP名」を実際のSSIDに置き換えて接続する。空白を含むSSIDも引用符で囲めば指定できる。

```sh
sudo nmcli --ask device wifi connect "Wi-Fi AP名"
```

パスワードは質問されたときに入力する。成功すると接続設定が保存され、次回以降にも利用できる。スマホのテザリングも同じ手順で追加する。Zero W / Zero 2 WではAPを2.4GHzに設定する。

接続状態とIPアドレスを確認する。

```sh
nmcli device status
nmcli connection show --active
ip -4 addr show wlan0
```

保存された接続先を一覧表示する。

```sh
nmcli connection show
```

既に保存したAPへ手動で切り替える場合は、一覧のNAMEを指定する。接続設定名はSSIDと異なる場合がある。

```sh
sudo nmcli --ask connection up "接続設定名"
```

**SSHで操作中にAPを切り替えると、SSH接続が切れる場合がある。** その場合はMacもPiへ到達できるネットワークへ接続し、新しいIPアドレスまたはホスト名でSSHし直す。AP追加は液晶側のキーボードから行うと接続切り替え後も操作を続けられる。

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

### Pi 4：再起動後も20pxを維持する設定

2026-10-12、Pi 4 / Raspberry Pi OS Lite 64bit（Trixie 13.7）、piscreen DRM液晶で、以下の設定後に再起動してもフォントサイズが維持されたことをユーザーが実機確認。

以下はすべて**Pi 4へSSH接続した画面**で実行する。

```sh
sudo apt install kbd console-setup-linux
sudo nano /etc/default/console-setup
```

既存の同名項目を次の値に変更する。項目がなければ追加し、重複させない。他の設定は残す。

```ini
CHARMAP="UTF-8"
CODESET="Lat15"
FONTFACE="Terminus"
FONTSIZE="10x20"
```

`10x20`は幅10・高さ20ピクセル。保存後に適用する：

```sh
sudo setupcon --save-only
sudo systemctl restart console-setup.service
sudo systemctl restart piscreen-console.service
```

液晶切り替え用の `/usr/local/sbin/piscreen-console.py` にも、`chvt`実行直後に次の処理を入れておく。行頭の字下げは既存のsubprocess.run行と揃える。

```python
        subprocess.run([
            'setfont', '-C', '/dev/tty1',
            '/usr/share/consolefonts/Lat15-Terminus20x10.psf.gz'
        ], check=True)
```

確認：

```sh
grep -A4 setfont /usr/local/sbin/piscreen-console.py
systemctl status piscreen-console.service --no-pager -l
sudo reboot
```

HDMIを外した状態で、液晶のログイン画面が20pxで表示されることを確認する。一時的なsetfontだけでは起動時のconsole-setupに戻される場合があるため、標準設定と液晶切り替え後のフォントを一致させる。

**機種による違い：** Pi 4の上記サービスは `piscreen-console.service`。Zero 2 Wの同梱セットアップは `mhs-console.service` と `/usr/local/lib/raspi-mobile/mhs-console.py` を使用する。サービス名・ファイル名を取り違えない。Pi 4用サービスは今回Pi上で手動作成したもので、このリポジトリのinstall.shはZero 2 W向けのまま。

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

## ケース設計ファイル

ケース設計の保存先は `case/`。最新版はV4で、本体・蓋のSTL、再生成用Pythonスクリプト、寸法メモをまとめている。今後の設計変更もこのフォルダーで管理する。詳細は [case/README.md](case/README.md) を参照。
