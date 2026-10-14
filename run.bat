@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto go
echo Environnement absent : installation en cours...
call install.bat auto
if errorlevel 1 exit /b 1

:go
echo Application disponible sur http://127.0.0.1:5000
echo Fermer cette fenêtre ou appuyer sur Ctrl+C pour arrêter.
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py
echo.
echo Le serveur est arrêté.
pause
