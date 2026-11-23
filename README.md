# local-tools

業務を自動化するローカル実行ツール集(Windows向け・Python未導入でも使えるREADME付き)。

```
local-tools/
├── template/        ← 新しいツールを作るときはこのフォルダをコピーする
├── 01-file-organizer/   (例: 自作のファイル整理ツール)
├── 02-typo-checker/     (例: Gemini連携の誤字脱字チェック)
└── ...
```

## 新しいツールの作り方
1. `template/` を `NN-ツール名/` としてコピー
2. `app.py` の `run_task()` を書き換える
3. `static/index.html` の見た目・ボタンを調整
4. `README.md` のタイトルと説明を書き換える
5. `start.bat` をダブルクリックして動作確認

各ツールのフォルダだけで完結するように作っています(共通ライブラリは持たない)。
