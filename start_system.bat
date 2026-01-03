@echo off
cd /d %~dp0

call venv\Scripts\activate

echo Checking tap configuration...
python -m app.check_taps > count.txt
set /p TAPCOUNT=<count.txt
del count.txt

if "%TAPCOUNT%"=="0" (
    echo No taps found — opening setup form...
    start "SETUP" cmd /k "python -m app.setup_form"
)

echo Starting core services...

start "SIMULATOR" cmd /k "python -m app.simulate"
start "PROCESSOR" cmd /k "python -m app.processor"
start "DASHBOARD" cmd /k "python -m app.dashboard"

pause
