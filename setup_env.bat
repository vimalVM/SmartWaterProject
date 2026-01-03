@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Environment ready!
echo Next time just run start_system.bat

pause
