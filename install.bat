@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo === Installation : suppression d'arrière-plan ===
echo.

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY goto nopython

%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 goto nopython

if exist ".venv\Scripts\python.exe" goto venvok
echo Création de l'environnement virtuel...
%PY% -m venv .venv
if errorlevel 1 goto fail

:venvok
echo Installation des dépendances...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail

echo.
echo Installation terminée.
echo Le modèle de segmentation, environ 1,5 Go, sera téléchargé une seule fois lors du premier traitement local.
echo Lancer ensuite l'application avec run.bat.
echo.
if not "%~1"=="auto" pause
exit /b 0

:nopython
echo ERREUR : Python 3.10 ou supérieur est introuvable.
echo Installer Python depuis https://www.python.org/downloads/ en cochant "Add python.exe to PATH", puis relancer ce script.
echo.
pause
exit /b 1

:fail
echo.
echo ERREUR : l'installation a échoué. Vérifier la connexion Internet, puis relancer ce script.
echo.
pause
exit /b 1
