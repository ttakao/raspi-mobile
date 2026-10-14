# ケース設計

このフォルダーをケース設計の保存先とする。現在の版はV4。今後の修正とSTL出力もここで行う。

- `build_case.py`：V4本体と蓋の設計・STL生成スクリプト。旧作業フォルダーへの依存なし。
- `ssh_case_v4_body.stl`：本体。
- `ssh_case_v4_lid.stl`：蓋。
- `ssh_case_v4_notes.txt`：寸法、暫定位置、印刷と検証の注意。

内寸90 × 90 × 33mm。上部ネジ2本、下部差し込み爪2か所。試験片では0.4mmの隙間がすっと入り、この寸法を採用。V4本体の印刷・実機組み込みは未確認。

## 再生成

このフォルダーで実行する。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python build_case.py
```

同じフォルダーのV4 STLを上書きする。形状の閉鎖性・単一連結・閉じた組立位置での重複ゼロをチェックする。実際の開閉・部品干渉・印刷性の確認を代替するものではない。

2026-10-14：液晶窓とスイッチ穴の左右を反転し、本体STLのみ更新。蓋は変更なし。`build_case.py --body-only` で本体だけを再生成できる。
