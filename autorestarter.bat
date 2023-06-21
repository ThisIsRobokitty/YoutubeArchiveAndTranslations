call venv\Scripts\activate.bat

:start

python archive_script.py

echo (%time%) Server crashed -- Restarting.

goto start

call venv\Scripts\deactivate.bat