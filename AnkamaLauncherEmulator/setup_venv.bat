@echo off
set VENV_PATH=.venv
set ACTIVATE_FILE=%VENV_PATH%\Scripts\activate.bat

findstr /C:"set PYTHONPATH=." "%ACTIVATE_FILE%" >nul
if errorlevel 1 (
    echo set PYTHONPATH=. >> "%ACTIVATE_FILE%"
    echo PYTHONPATH added to %ACTIVATE_FILE%
) else (
    echo PYTHONPATH already in %ACTIVATE_FILE%
)