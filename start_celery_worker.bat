@echo off
echo ========================================
echo Starting Celery Worker
echo ========================================
echo.

cd /d "%~dp0"
python -m celery -A backend.tasks.celery_config worker --loglevel=info --pool=solo

pause

