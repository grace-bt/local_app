"""
ローカル業務自動化ツールのテンプレート(Flask版)

読む順番のおすすめ:
  1. 設定        … ポートやAPIキーの読み込み
  2. 安全チェック … 他のサイトから勝手に叩かれないための仕組み
  3. run_task    … ★ここに自分の処理を書く(ファイル整理など)
  4. ask_gemini  … Gemini APIを呼ぶ部品(使わなくてもOK)
  5. ルーティング … 画面(static/*.html)とAPIの入口
"""
import os
import secrets
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request

# ---------------------------------------------------------------
# 1. 設定
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")  # .env の中身を環境変数として読み込む

PORT = int(os.getenv("PORT", "8765"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

# 起動するたびに作り直す合言葉。画面(static/*.html)にだけ埋め込まれる。
TOKEN = secrets.token_urlsafe(16)

app = Flask(__name__)


# ---------------------------------------------------------------
# 2. 安全チェック(APIを呼ぶ前に毎回実行される)
# ---------------------------------------------------------------
@app.before_request
def check_request():
    if not request.path.startswith("/api/"):
        return  # 画面そのものはチェック不要

    # (a) 宛先が自分のPC(127.0.0.1 / localhost)以外ならお断り
    #     → DNSリバインディングという攻撃への対策
    host = request.host.split(":")[0]
    if host not in ("127.0.0.1", "localhost"):
        abort(403)

    # (b) 合言葉(トークン)が違えばお断り
    #     → 別のWebサイトのJavaScriptから勝手に実行されるのを防ぐ
    sent = request.headers.get("X-Token", "")
    if not secrets.compare_digest(sent, TOKEN):
        abort(403)


# ---------------------------------------------------------------
# 3. ★ここに自分の処理を書く
# ---------------------------------------------------------------
def run_task(text: str) -> dict:
    """ボタン「処理を実行」で呼ばれる。

    今はサンプルとして文字数を数えるだけ。
    ファイル整理などを作るときは、この中身を書き換える。
    戻り値はdict(辞書)にすると、そのまま画面に表示される。
    """
    return {
        "受け取った文字数": len(text),
        "実行した時刻": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ---------------------------------------------------------------
# 4. Gemini APIを呼ぶ部品
# ---------------------------------------------------------------
class UserFacingError(Exception):
    """画面にそのまま見せてよいエラー(初心者向けの説明つき)"""


def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise UserFacingError(
            "APIキーが未設定です。.env ファイルに GEMINI_API_KEY=... を書いてください。"
        )
    from google import genai  # 使うときだけ読み込む

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text or "(空の応答でした)"
    except Exception as e:  # 無料枠の上限超過・キー間違いなどをまとめて受ける
        raise UserFacingError(f"Gemini APIでエラーが出ました: {e}")


# ---------------------------------------------------------------
# 5. ルーティング(URLと処理の対応表)
# ---------------------------------------------------------------
@app.get("/")
@app.get("/<name>.html")
def page(name="index"):
    """static/ 内の .html を返す。新しいページはファイルを足すだけでOK。"""
    path = (BASE_DIR / "static" / f"{name}.html").resolve()
    # static フォルダの外は読ませない(../ を使った侵入対策)
    if not path.is_relative_to(BASE_DIR / "static") or not path.is_file():
        abort(404)
    html = path.read_text(encoding="utf-8")
    return html.replace("__TOKEN__", TOKEN)  # 合言葉を画面に埋め込む(無いページは何も起きない)


@app.post("/api/run")
def api_run():
    text = (request.get_json(silent=True) or {}).get("text", "")
    return jsonify(ok=True, result=run_task(text))


@app.post("/api/gemini")
def api_gemini():
    prompt = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    if not prompt:
        return jsonify(ok=False, message="質問が空です。"), 400
    try:
        return jsonify(ok=True, result=ask_gemini(prompt))
    except UserFacingError as e:
        return jsonify(ok=False, message=str(e)), 500


# ---------------------------------------------------------------
# 起動
# ---------------------------------------------------------------
if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}/"
    print(f"起動しました: {url}  (止めるときはこの黒い画面を閉じる)")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()  # 1秒後にブラウザを開く
    # host="127.0.0.1" … 自分のPCからのアクセスだけ受け付ける(重要)
    app.run(host="127.0.0.1", port=PORT, debug=False)
