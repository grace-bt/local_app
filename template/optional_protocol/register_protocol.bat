@echo off
rem 【オプション・未検証】Webサイトのボタンから start.bat を起動できるようにする設定。
rem 1回だけダブルクリックで実行。管理者権限は不要(HKCU に書き込むだけ)。
rem サイト側は <a href="localtool://start">起動</a> と書く。
rem 注意: 引数(%1)はあえて start.bat に渡さない。URLの中身を処理に使わせないため。
chcp 65001 >nul
set "TARGET=%~dp0..\start.bat"

reg add "HKCU\Software\Classes\localtool" /ve /d "URL:LocalTool Protocol" /f
reg add "HKCU\Software\Classes\localtool" /v "URL Protocol" /d "" /f
reg add "HKCU\Software\Classes\localtool\shell\open\command" /ve /d "\"%TARGET%\"" /f

echo 登録しました。ブラウザで localtool://start を開くと確認ダイアログが出ます。
pause
